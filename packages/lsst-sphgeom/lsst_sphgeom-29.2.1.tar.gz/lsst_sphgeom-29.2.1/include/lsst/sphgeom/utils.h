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

#ifndef LSST_SPHGEOM_UTILS_H_
#define LSST_SPHGEOM_UTILS_H_

/// \file
/// \brief This file declares miscellaneous utility functions.

#include "Angle.h"


namespace lsst {
namespace sphgeom {

// Forward declarations
class Vector3d;
class UnitVector3d;

/// Let p be the unit vector closest to v that lies on the plane with
/// normal n in the direction of the cross product of a and b. If p is in the
/// interior of the great circle segment from a to b, then this function
/// returns the squared chord length between p and v. Otherwise it returns 4 -
/// the maximum squared chord length between any pair of points on the unit
/// sphere.
double getMinSquaredChordLength(Vector3d const & v,
                                Vector3d const & a,
                                Vector3d const & b,
                                Vector3d const & n);

/// Let p be the unit vector furthest from v that lies on the plane with
/// normal n in the direction of the cross product of a and b. If p is in the
/// interior of the great circle segment from a to b, then this helper function
/// returns the squared chord length between p and v. Otherwise it returns 0 -
/// the minimum squared chord length between any pair of points on the sphere.
double getMaxSquaredChordLength(Vector3d const & v,
                                Vector3d const & a,
                                Vector3d const & b,
                                Vector3d const & n);

/// `getMinAngleToCircle` returns the minimum angular separation between a
/// point at latitude x and the points on the circle of constant latitude c.
inline Angle getMinAngleToCircle(Angle x, Angle c) {
    return abs(x - c);
}

/// `getMaxAngleToCircle` returns the maximum angular separation between a
/// point at latitude x and the points on the circle of constant latitude c.
inline Angle getMaxAngleToCircle(Angle x, Angle c) {
    Angle a = getMinAngleToCircle(x, c);
    if (abs(x) <= abs(c)) {
        return a + Angle(PI) - 2.0 * abs(c);
    }
    if (a < abs(x)) {
        return Angle(PI) - 2.0 * abs(c) - a;
    }
    return Angle(PI) + 2.0 * abs(c) - a;
}

/// `getWeightedCentroid` returns the center of mass of the given spherical
/// triangle (assuming a uniform mass distribution over the triangle surface),
/// weighted by the triangle area.
Vector3d getWeightedCentroid(UnitVector3d const & v0,
                             UnitVector3d const & v1,
                             UnitVector3d const & v2);

}} // namespace lsst::sphgeom

#endif // LSST_SPHGEOM_UTILS_H_
