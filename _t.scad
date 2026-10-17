use <Animals-Zvirata/Boar-PraseDivoke/boar_stamp.scad>
linear_extrude(base_h) base_shape();
translate([0,0,base_h-0.2]) linear_extrude(handle_h+0.2) offset(r=handle_r) offset(delta=-handle_r) square([handle_w, handle_d], center=true);
