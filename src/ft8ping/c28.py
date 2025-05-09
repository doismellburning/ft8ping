"""
Python port of ft4_ft8_public/std_call_to_c28.f90,
public domain software (per https://wsjt.sourceforge.io/FT4_FT8_QEX.pdf)
from http://www.arrl.org/QEXfiles
"""

"""
Original source:

program std_call_to_c28

  parameter (NTOKENS=2063592,MAX22=4194304)
  character*6 call_std
  character a1*37,a2*36,a3*10,a4*27
  data a1/' 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'/
  data a2/'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'/
  data a3/'0123456789'/
  data a4/' ABCDEFGHIJKLMNOPQRSTUVWXYZ'/

  nargs=iargc()
  if(nargs.ne.1) then
     print*,'Usage:   std_call_to_c28 <call_std>'
     print*,'Example: std_call_to_c28 K1ABC'
     go to 999
  endif
  call getarg(1,call_std)
  call_std=adjustr(call_std)
  i1=index(a1,call_std(1:1))-1
  i2=index(a2,call_std(2:2))-1
  i3=index(a3,call_std(3:3))-1
  i4=index(a4,call_std(4:4))-1
  i5=index(a4,call_std(5:5))-1
  i6=index(a4,call_std(6:6))-1
  n28=NTOKENS + MAX22 + 36*10*27*27*27*i1 + 10*27*27*27*i2 + &
       27*27*27*i3 + 27*27*i4 + 27*i5 + i6

  write(*,1000) call_std,n28
1000 format('Callsign: ',a6,2x,'c28 as decimal integer:',i10)

999 end program std_call_to_c28
"""


def main():
    import sys

    if len(sys.argv) != 2:
        print("Usage:   std_call_to_c28 <call_std>")
        print("Example: std_call_to_c28 K1ABC")
        return

    call_std = sys.argv[1]
    n28 = call_to_c28(call_std)

    print(f"Callsign: {call_std}  c28 as decimal integer: {n28}")


def call_to_c28(call: str):
    NTOKENS = 2063592
    MAX22 = 4194304

    a1 = " 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    a2 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    a3 = "0123456789"
    a4 = " ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    call_std = call.rjust(6)

    # Fortran's index() returns position (1-based) or 0 if not found
    # Python's find() returns position (0-based) or -1 if not found
    i1 = a1.find(call_std[0])
    i2 = a2.find(call_std[1])
    i3 = a3.find(call_std[2])
    i4 = a4.find(call_std[3])
    i5 = a4.find(call_std[4])
    i6 = a4.find(call_std[5])

    # No need to subtract 1 as in the original code
    # Fortran: index()-1, Python: find() directly

    n28 = (
        NTOKENS
        + MAX22
        + 36 * 10 * 27 * 27 * 27 * i1
        + 10 * 27 * 27 * 27 * i2
        + 27 * 27 * 27 * i3
        + 27 * 27 * i4
        + 27 * i5
        + i6
    )

    return n28


if __name__ == "__main__":
    main()
