/*
 * This file is part of sphgeom.
 *
 * Developed for the LSST Data Management System.
 * This product includes software developed by the LSST Project
 * (http://www.lsst.org).
 * See the COPYRIGHT file at the top-level directory of this distribution
 * for details of code ownership.
 *
 * This software is dual licensed under the GNU General Public License and also
 * under a 3-clause BSD license. Recipients may choose which of these licenses
 * to use; please see the files gpl-3.0.txt and/or bsd_license.txt,
 * respectively.  If you choose the GPL option then the following text applies
 * (but note that there is still no warranty even if you opt for BSD instead):
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

/// \file
/// \brief This file contains the Mq3cPixelization class implementation.

#include "lsst/sphgeom/Mq3cPixelization.h"

#include <stdexcept>

#include "lsst/sphgeom/ConvexPolygon.h"
#include "lsst/sphgeom/curve.h"
#include "lsst/sphgeom/UnitVector3d.h"

#include "PixelFinder.h"
#include "Q3cPixelizationImpl.h"


namespace lsst {
namespace sphgeom {

namespace {

// See commentary in Q3cPixelizationImpl.h for an explanation of
// these lookup tables.

constexpr std::uint8_t UNUSED = 255;

alignas(64) std::uint8_t const FACE_NUM[64] = {
         4,      4,      4,      4, UNUSED,      3, UNUSED, UNUSED,
    UNUSED, UNUSED,      0, UNUSED, UNUSED, UNUSED, UNUSED, UNUSED,
    UNUSED, UNUSED, UNUSED,      2, UNUSED,      3, UNUSED,      2,
    UNUSED, UNUSED,      0,      2, UNUSED, UNUSED, UNUSED,      2,
         5, UNUSED, UNUSED, UNUSED,      5,      3, UNUSED, UNUSED,
         5, UNUSED,      0, UNUSED,      5, UNUSED, UNUSED, UNUSED,
    UNUSED, UNUSED, UNUSED, UNUSED, UNUSED,      3, UNUSED, UNUSED,
    UNUSED, UNUSED,      0, UNUSED,      1,      1,      1,      1
};

std::uint8_t const FACE_COMP[6][4] = {
    {0, 1, 2, UNUSED}, {1, 2, 0, UNUSED}, {2, 0, 1, UNUSED},
    {0, 1, 2, UNUSED}, {1, 2, 0, UNUSED}, {2, 0, 1, UNUSED}
};

double const FACE_CONST[6][4] = {
    { 1.0,  1.0, -1.0, 0.0},
    { 1.0,  1.0,  1.0, 0.0},
    { 1.0, -1.0,  1.0, 0.0},
    {-1.0, -1.0,  1.0, 0.0},
    {-1.0, -1.0, -1.0, 0.0},
    {-1.0,  1.0, -1.0, 0.0}
};

// TODO: Fix and document this constant!
constexpr double DILATION = 1.0e-15;

// `wrapIndex` returns the modified-Q3C index for grid coordinates (face, s, t)
// at the given level. Both s and t may underflow or overflow by 1, i.e. wrap
// to an adjacent face.
std::uint64_t wrapIndex(int level,
                   int face,
                   std::uint32_t s,
                   std::uint32_t t)
{
    std::uint32_t const stMax = (static_cast<std::uint32_t>(1) << level) - 1;
    // Wrap until no more underflow or overflow is detected.
    while (true) {
        if (s == static_cast<std::uint32_t>(-1)) {
            face = (face + 4) % 6;
            s = stMax - t;
            t = stMax;
            continue;
        } else if (s > stMax) {
            face = (face + 1) % 6;
            s = t;
            t = 0;
            continue;
        } else if (t == static_cast<std::uint32_t>(-1)) {
            face = (face + 5) % 6;
            t = s;
            s = stMax;
            continue;
        } else if (t > stMax) {
            face = (face + 2) % 6;
            t = stMax - s;
            s = 0;
            continue;
        }
        break;
    }
    return (static_cast<std::uint64_t>(face + 10) << (2 * level)) |
           hilbertIndex(s, t, level);
}

int findNeighborhood(int level, std::uint64_t i, std::uint64_t * dst) {
    int const face = static_cast<int>(i >> (2 * level)) - 10;
    std::uint32_t s, t;
    std::tie(s, t) = hilbertIndexInverse(i, level);
    dst[0] = wrapIndex(level, face, s - 1, t - 1);
    dst[1] = wrapIndex(level, face, s    , t - 1);
    dst[2] = wrapIndex(level, face, s + 1, t - 1);
    dst[3] = wrapIndex(level, face, s - 1, t);
    dst[4] = i;
    dst[5] = wrapIndex(level, face, s + 1, t);
    dst[6] = wrapIndex(level, face, s - 1, t + 1);
    dst[7] = wrapIndex(level, face, s    , t + 1);
    dst[8] = wrapIndex(level, face, s + 1, t + 1);
    std::sort(dst, dst + 9);
    return static_cast<int>(std::unique(dst, dst + 9) - dst);
}

#if defined(NO_SIMD) || !defined(__x86_64__)
    void makeQuad(std::uint64_t i, int level, UnitVector3d * verts) {
        int const face = static_cast<int>(i >> (2 * level)) - 10;
        double const faceScale = FACE_SCALE[level];
        double u0, v0;
        std::uint32_t s, t;
        std::tie(s, t) = hilbertIndexInverse(i, level);
        std::tie(u0, v0) = gridToFace(
            level, static_cast<std::int32_t>(s), static_cast<std::int32_t>(t));
        double u1 = (u0 + faceScale) + DILATION;
        double v1 = (v0 + faceScale) + DILATION;
        u0 -= DILATION;
        v0 -= DILATION;
        std::tie(u0, v0) = atanApproxInverse(u0, v0);
        std::tie(u1, v1) = atanApproxInverse(u1, v1);
        verts[0] = faceToSphere(face, u0, v0, FACE_COMP, FACE_CONST);
        verts[1] = faceToSphere(face, u1, v0, FACE_COMP, FACE_CONST);
        verts[2] = faceToSphere(face, u1, v1, FACE_COMP, FACE_CONST);
        verts[3] = faceToSphere(face, u0, v1, FACE_COMP, FACE_CONST);
        // Even face numbers have right-handed uv coordinate systems,
        // odd face numbers have left-handed ones. This has to be taken
        // into account when generating pixel vertices, since convex
        // polygon vertices must be specified in counter-clockwise order.
        if ((face & 1) == 0) {
            std::swap(verts[1], verts[3]);
        }
    }
#else
    void makeQuad(std::uint64_t i, int level, UnitVector3d * verts) {
        int const face = static_cast<int>(i >> (2 * level)) - 10;
        __m128d faceScale = _mm_set1_pd(FACE_SCALE[level]);
        __m128d dilation = _mm_set1_pd(DILATION);
        __m128d u0v0 = gridToFace(level, hilbertIndexInverseSimd(i, level));
        __m128d u1v1 = _mm_add_pd(u0v0, faceScale);
        u0v0 = atanApproxInverse(_mm_sub_pd(u0v0, dilation));
        u1v1 = atanApproxInverse(_mm_add_pd(u1v1, dilation));
        verts[0] = faceToSphere(face, u0v0, FACE_COMP, FACE_CONST);
        verts[1] = faceToSphere(face, _mm_shuffle_pd(u1v1, u0v0, 2),
                                FACE_COMP, FACE_CONST);
        verts[2] = faceToSphere(face, u1v1, FACE_COMP, FACE_CONST);
        verts[3] = faceToSphere(face, _mm_shuffle_pd(u0v0, u1v1, 2),
                                FACE_COMP, FACE_CONST);
        if ((face & 1) == 0) {
            std::swap(verts[1], verts[3]);
        }
    }
#endif


// `Mq3cPixelFinder` locates modified-Q3C pixels that intersect a region.
//
// For now, we always begin with a loop over the root cube faces. For small
// regions, this could be made significantly faster by computing the modified
// Q3C index of the region bounding circle center, and looping over that pixel
// and its neighbors.
//
// The subdivision level for the initial index computation would have to be
// chosen such that the 8 or 9 pixel neighborhood of the center pixel is
// guaranteed to contain the bounding circle. The minimum angular pixel width
// could be precomputed per level. Alternatively, there is some constant W
// such that the minimum angle between two points separated by at least one
// pixel is greater than W * 2^-L at level L. Given the bounding circle
// radius R, the subdivision level L of the initial neighborhood is the binary
// exponent of W/R (and can be extracted by calling std::frexp).
//
// Finding W and implementing the above is left as a future optimization.
template <typename RegionType, bool InteriorOnly>
class Mq3cPixelFinder: public detail::PixelFinder<
    Mq3cPixelFinder<RegionType, InteriorOnly>, RegionType, InteriorOnly, 4>
{
private:
    using Base = detail::PixelFinder<
        Mq3cPixelFinder<RegionType, InteriorOnly>, RegionType, InteriorOnly, 4>;
    using Base::visit;

public:
    Mq3cPixelFinder(RangeSet & ranges,
                    RegionType const & region,
                    int level,
                    size_t maxRanges):
        Base(ranges, region, level, maxRanges)
    {}

    void operator()() {
        UnitVector3d pixel[4];
        // Loop over cube faces
        for (std::uint64_t f = 10; f < 16; ++f) {
            makeQuad(f, 0, pixel);
            visit(pixel, f, 0);
        }
    }

    void subdivide(UnitVector3d const *, std::uint64_t i, int level) {
        UnitVector3d pixel[4];
        ++level;
        for (std::uint64_t c = i * 4; c != i * 4 + 4; ++c) {
            makeQuad(c, level, pixel);
            visit(pixel, c, level);
        }
    }
};

} // unnamed namespace


int Mq3cPixelization::level(std::uint64_t i) {
    // A modified Q3C index consists of 4 bits encoding the root cube face
    // (10 - 15), followed by 2l bits, where each of the l bit pairs encodes
    // a child index (0-3), and l is the desired level.
    int j = log2(i);
    // The level l is derivable from the index j of the MSB of i. For i to
    // be valid, j must be an odd integer > 1 and the upper 4 bits of i must
    // be at least 10.
    if ((j & 1) == 0 || (j == 1) || ((i >> (j - 3)) < 10)) {
        return -1;
    }
    return (j - 3) >> 1;
}

ConvexPolygon Mq3cPixelization::quad(std::uint64_t i) {
    int l = level(i);
    if (l < 0 || l > MAX_LEVEL) {
        throw std::invalid_argument("Invalid modified-Q3C index");
    }
    UnitVector3d verts[4];
    makeQuad(i, l, verts);
    return ConvexPolygon(verts[0], verts[1], verts[2], verts[3]);
}

std::vector<std::uint64_t> Mq3cPixelization::neighborhood(std::uint64_t i) {
    int l = level(i);
    if (l < 0 || l > MAX_LEVEL) {
        throw std::invalid_argument("Invalid modified-Q3C index");
    }
    std::uint64_t indexes[9];
    int n = findNeighborhood(l, i, indexes);
    return std::vector<std::uint64_t>(indexes, indexes + n);
}

std::string Mq3cPixelization::asString(std::uint64_t i) {
    static char const FACE_NORM[6][2] = {
        {'-', 'Z'}, {'+', 'X'}, {'+', 'Y'},
        {'+', 'Z'}, {'-', 'X'}, {'-', 'Y'},
    };
    char s[MAX_LEVEL + 2];
    int l = level(i);
    if (l < 0 || l > MAX_LEVEL) {
        throw std::invalid_argument("Invalid modified-Q3C index");
    }
    // Print in base-4, from least to most significant digit.
    char * p = s + (sizeof(s) - 1);
    for (; l > 0; --l, --p, i >>= 2) {
        *p = '0' + (i & 3);
    }
    // The remaining bits correspond to the cube face.
    --p;
    p[0] = FACE_NORM[i - 10][0];
    p[1] = FACE_NORM[i - 10][1];
    return std::string(p, sizeof(s) - static_cast<size_t>(p - s));
}

Mq3cPixelization::Mq3cPixelization(int level) : _level{level} {
    if (level < 0 || level > MAX_LEVEL) {
        throw std::invalid_argument(
            "Modified-Q3C subdivision level not in [0, 30]");
    }
}

std::unique_ptr<Region> Mq3cPixelization::pixel(std::uint64_t i) const {
    std::uint64_t f = i >> (2 * _level);
    if (f < 10 || f > 15) {
        throw std::invalid_argument("Invalid modified-Q3C index");
    }
    UnitVector3d verts[4];
    makeQuad(i, _level, verts);
    return std::unique_ptr<Region>(
        new ConvexPolygon(verts[0], verts[1], verts[2], verts[3]));
}

#if defined(NO_SIMD) || !defined(__x86_64__)
    std::uint64_t Mq3cPixelization::index(UnitVector3d const & p) const {
        int face = faceNumber(p, FACE_NUM);
        double w = std::fabs(p(FACE_COMP[face][2]));
        double u = (p(FACE_COMP[face][0]) / w) * FACE_CONST[face][0];
        double v = (p(FACE_COMP[face][1]) / w) * FACE_CONST[face][1];
        std::tie(u, v) = atanApprox(u, v);
        std::tuple<std::int32_t, std::int32_t> g = faceToGrid(_level, u, v);
        std::uint64_t h = hilbertIndex(static_cast<std::uint32_t>(std::get<0>(g)),
                                  static_cast<std::uint32_t>(std::get<1>(g)),
                                  _level);
        return (static_cast<std::uint64_t>(face + 10) << (2 * _level)) | h;
    }
#else
    std::uint64_t Mq3cPixelization::index(UnitVector3d const & p) const {
        int face = faceNumber(p, FACE_NUM);
        __m128d ww = _mm_set1_pd(p(FACE_COMP[face][2]));
        __m128d uv = _mm_set_pd(p(FACE_COMP[face][1]), p(FACE_COMP[face][0]));
        uv = _mm_mul_pd(
            _mm_div_pd(uv, _mm_andnot_pd(_mm_set_pd(-0.0, -0.0), ww)),
            _mm_set_pd(FACE_CONST[face][1], FACE_CONST[face][0])
        );
        __m128i st = faceToGrid(_level, atanApprox(uv));
        std::uint64_t h = hilbertIndex(st, _level);
        return (static_cast<std::uint64_t>(face + 10) << (2 * _level)) | h;
    }
#endif

RangeSet Mq3cPixelization::_envelope(Region const & r, size_t maxRanges) const {
    return detail::findPixels<Mq3cPixelFinder, false>(r, maxRanges, _level, universe());
}

RangeSet Mq3cPixelization::_interior(Region const & r, size_t maxRanges) const {
    return detail::findPixels<Mq3cPixelFinder, true>(r, maxRanges, _level, universe());
}

}} // namespace lsst::sphgeom
