module superconductors
  !! Module containing superconducter critical surfaces and conductor data
#ifndef dp
  use, intrinsic :: iso_fortran_env, only: dp=>real64
#endif
  implicit none
contains

!--------------------------------------------------------------------

subroutine wstsc(temperature,bmax,strain,bc20max,tc0max,jcrit,bcrit,tcrit)

    !! Implementation of WST Nb3Sn critical surface implementation
    !! author: J Morris, CCFE, Culham Science Centre
    !! temperature : input real : SC temperature (K)
    !! bmax : input real : Magnetic field at conductor (T)
    !! strain : input real : Strain in superconductor
    !! bc20max : input real : Upper critical field (T) for superconductor
    !! at zero temperature and strain
    !! tc0max : input real : Critical temperature (K) at zero field and strain
    !! jcrit : output real : Critical current density in superconductor (A/m2)
    !! bcrit : output real : Critical field (T)
    !! tcrit : output real : Critical temperature (K)
    !! This routine calculates the critical current density and
    !! temperature in the superconducting TF coils using the
    !! WST Nb3Sn critical surface model.
    !! V. Corato et al, "Common operating values for DEMO magnets design for 2016",
    !! https://scipub.euro-fusion.org/wp-content/uploads/eurofusion/WPMAGREP16_16565_submitted.pdf
    !
    ! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    use error_handling, only: fdiags, report_error
    use maths_library, only: variable_error
    implicit none

    ! Arguments
    real(dp), intent(in) :: temperature, bmax, strain, bc20max, tc0max
    real(dp), intent(out) :: jcrit, bcrit, tcrit

    ! Local variables

    ! Scaling constant C [AT/mm2]
    real(dp), parameter :: csc = 83075.0D0
    ! Low field exponent p
    real(dp), parameter :: p = 0.593D0
    ! High field exponent q
    real(dp), parameter :: q = 2.156D0
    ! Strain fitting constant C_{a1}
    real(dp), parameter :: ca1 = 50.06D0
    ! Strain fitting constant C_{a2}
    real(dp), parameter :: ca2 = 0.0D0
    ! epsilon_{0,a}
    real(dp), parameter :: eps0a = 0.00312D0

    !real(dp), parameter :: epsmax = -1.1D-3  !  epsilon_{max} (not used)

    real(dp) :: bred, epssh, t, bc20eps, &
    tc0eps, bzero, strfun, jc1, jc2, jc3, scalefac

    ! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    !  $\epsilon_{sh}$
    epssh = (ca2*eps0a)/(sqrt(ca1**2 - ca2**2))

    !  Strain function $s(\epsilon)$
    !  0.83 < s < 1.0, for -0.005 < strain < 0.005
    strfun = sqrt(epssh**2 + eps0a**2) - sqrt((strain-epssh)**2 + eps0a**2)
    strfun = strfun*ca1 - ca2*strain
    strfun = 1.0D0 + (1.0D0/(1.0D0 - ca1*eps0a))*strfun
    if(strfun<0.d0)write(*,*)'subroutine wstsc: strfun<0.d0. strfun =', strfun, ', strain = ',strain

    !  $B^*_{C2} (0,\epsilon)$
    bc20eps = bc20max*strfun

    !  $T^*_C (0,\epsilon)$
    tc0eps = tc0max * strfun**(1.0D0/3.0D0)

    !  Reduced temperature
    !  Should remain < 1 for temperature < 0.94*tc0max (i.e. 15 kelvin for i_tf_sc_mat=1)

    if (temperature/tc0eps >= 1.0D0) then
        fdiags(1) = temperature ; fdiags(2) = tc0eps
        call report_error(159)
    end if
    ! t = min(thelium/tc0eps, 0.9999D0)
    t = temperature/tc0eps

    !  Reduced magnetic field at zero temperature
    !  Should remain < 1 for bmax < 0.83*bc20max (i.e. 27 tesla for i_tf_sc_mat=1)

    if (bmax/bc20eps >= 1.0D0) then
        fdiags(1) = bmax ; fdiags(2) = bc20eps
        call report_error(160)
    end if

    ! bzero = min(bmax/bc20eps, 0.9999D0)
    bzero = bmax/bc20eps

    if (bzero < 1.0d0) then
        !  Critical temperature (K)
        tcrit = tc0eps * (1.0D0 - bzero)**(1.0D0/1.52D0)
    else
        ! Allow bzero > 1, fudge to give real (negative) value of tcrit
        ! This generates a real (negative) and continuous (but not differentiable)
        ! function of bzero.
        tcrit = tc0eps
    end if



    !  Critical field (T). Negative if normalised temperature t>1
    if(t>0.0d0)then
        bcrit = bc20eps * (1.0D0 - t**1.52D0)
    else
        ! Allow t<0, fudge to give real value of bcrit
        bcrit = bc20eps * (1.0D0 - t)
    end if

    !  Reduced magnetic field, restricted to be < 1
    if (bmax/bcrit >= 1.0D0) then
        fdiags(1) = bmax ; fdiags(2) = bcrit
        call report_error(161)
    end if
    ! bred = min(bmax/bcrit, 0.9999D0)
    bred = bmax/bcrit

    if ((bred>0.0d0).and.(bred < 1.0d0)) then
        jc3 = bred**p * (1.0D0-bred)**q  !  bred must be < 1 to avoid NaNs
    else
        ! Allow bred > 1 or <0, fudge to give real (negative) value of jc3
        ! This generates a real (negative) and continuous (but not differentiable)
        ! function of bred.
        jc3 = bred * (1.0D0-bred)
        if(variable_error(jc3))then
            write(*,'(a24, 8(a12,es12.3))')'jc3 jcrit is NaN.',' bred=',bred, ' bmax=',bmax, ' bcrit=',bcrit, ' t=',t
            stop 1
        end if
    end if

    !  Critical current density in superconductor (A/m2)
    jc1 = (csc/bmax)*strfun

    if(t>0.0d0)then
        jc2 = (1.0D0-t**1.52D0) * (1.0D0-t**2)
    else
        ! Allow t<0, fudge to give real value of jc2
        ! This generates a real and continuous (but not differentiable) function of t.
        jc2 = (1.0D0-t) * (1.0D0-t**2)
    end if

    ! jc3 = bred**p * (1.0D0-bred)**q  !  bred must be < 1 to avoid NaNs

    ! scale from mm2 to m2
    scalefac = 1.0D6

    jcrit = jc1 * jc2 * jc3*scalefac
    if(variable_error(jcrit))then
        write(*,'(a24, 8(a12,es12.3))')'WST jcrit is NaN.',' jc1=',jc1, ' jc2=',jc2, ' jc3=',jc3, ' t=',t
        write(*,'(a24, 8(a12,es12.3))')'T=',T,' bmax=',bmax,' strain=',strain,' bc20max=',bc20max, &
                                       ' tc0max=',tc0max,'jcrit=',jcrit,' bcrit=',bcrit,' tcrit=', tcrit
        stop 1
    end if

end subroutine wstsc
!--------------------------------------------------------------------------

subroutine croco(jcritsc, croco_strand_area, croco_strand_critical_current, &
    conductor_copper_area, conductor_copper_fraction, conductor_copper_bar_area, &
    conductor_hastelloy_area, conductor_hastelloy_fraction, conductor_helium_area, &
    conductor_helium_fraction, conductor_solder_area, conductor_solder_fraction, &
    conductor_rebco_area, conductor_rebco_fraction, conductor_critical_current, &
    conductor_area, croco_od,croco_thick)

    !! "CroCo" (cross-conductor) strand and cable design for
    !! "REBCO" 2nd generation HTS superconductor
    ! Updated 13/11/18 using data from Lewandowska et al 2018.

    use rebco_variables, only: copper_area, copper_thick, croco_id, &
      hastelloy_area, hastelloy_thickness, rebco_area, solder_area, &
      stack_thickness, tape_thickness, tape_width, tapes, rebco_thickness
    use resistive_materials, only: volume_fractions, supercon_strand
    use constants, only: pi
    implicit none
    real(dp), intent(in) ::jcritsc
    real(dp) :: d, scaling, croco_od, croco_thick

    ! conductor
    real(dp), intent(inout) :: conductor_copper_area,  conductor_copper_fraction
    real(dp), intent(inout) :: conductor_copper_bar_area
    real(dp), intent(inout) :: conductor_hastelloy_area, conductor_hastelloy_fraction
    real(dp), intent(inout) :: conductor_helium_area, conductor_helium_fraction
    real(dp), intent(inout) :: conductor_solder_area, conductor_solder_fraction
    real(dp), intent(inout) :: conductor_rebco_area,  conductor_rebco_fraction
    real(dp), intent(inout) :: conductor_critical_current
    real(dp), intent(in) :: conductor_area

    ! croco_strand
    real(dp), intent(inout) :: croco_strand_area
    real(dp), intent(inout) :: croco_strand_critical_current


    ! Define local alias
    d = croco_od
    !d = conductor_width / 3.0d0 - thwcndut * ( 2.0d0 / 3.0d0 )

    croco_id = d - 2.0d0 * croco_thick !scaling * 5.4d-3
    if (croco_id <= 0.0d0) then
        write(*,*) 'Warning: negitive inner croco diameter!'
        write(*,*)'croco_id =', croco_id, ',croco_thick = ', croco_thick, ', croco_od =', croco_od
    end if
    ! Define the scaling factor for the input REBCO variable
    ! Ratio of new croco inner diameter and fixed base line value
    scaling = croco_id / 5.4d-3
    tape_width = scaling * 3.75d-3
    ! Properties of a single strand
    tape_thickness = rebco_thickness + copper_thick + hastelloy_thickness
    stack_thickness = sqrt(croco_id**2 - tape_width**2)
    tapes = stack_thickness / tape_thickness

    copper_area = pi * croco_thick * d - pi * croco_thick**2 &  ! copper tube
                  + copper_thick*tape_width*tapes          ! copper in tape
    hastelloy_area = hastelloy_thickness * tape_width * tapes
    solder_area = pi / 4.0d0 * croco_id**2 - stack_thickness * tape_width

    rebco_area = rebco_thickness * tape_width * tapes
    croco_strand_area =  pi / 4.0d0 * d**2
    croco_strand_critical_current = jcritsc * rebco_area

    ! Conductor properties
    !conductor%number_croco = conductor%acs*(1d0-cable_helium_fraction-copper_bar)/croco_strand_area
    conductor_critical_current = croco_strand_critical_current * 6.0d0
    ! Area of core = area of strand
    conductor_copper_bar_area = croco_strand_area
    conductor_copper_area = copper_area * 6.0d0 + conductor_copper_bar_area
    conductor_copper_fraction = conductor_copper_area / conductor_area

    ! Helium area is set by the user.
    !conductor_helium_area = cable_helium_fraction * conductor_acs
    conductor_helium_area = pi / 2.0d0 * d**2
    conductor_helium_fraction = conductor_helium_area / conductor_area

    conductor_hastelloy_area = hastelloy_area * 6.0d0
    conductor_hastelloy_fraction = conductor_hastelloy_area / conductor_area

    conductor_solder_area = solder_area * 6.0d0
    conductor_solder_fraction = conductor_solder_area / conductor_area

    conductor_rebco_area = rebco_area * 6.0d0
    conductor_rebco_fraction = conductor_rebco_area / conductor_area

end subroutine croco

end module superconductors
