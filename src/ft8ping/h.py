import sys

"""
Python port of ft4_ft8_public/hashcodes.f90,
public domain software (per https://wsjt.sourceforge.io/FT4_FT8_QEX.pdf)
from http://www.arrl.org/QEXfiles
"""

"""
Original source:

program hashcodes

  parameter (NTOKENS=2063592)
  integer*8 nprime,n8(3)
  integer nbits(3),ihash(3)
  character*11 callsign
  character*38 c
  data c/' 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ/'/
  data nprime/47055833459_8/,nbits/10,12,22/

  nargs=iargc()
  if(nargs.ne.1) then
     print*,'Usage:    hashcodes <callsign>'
     print*,'Examples: hashcodes PJ4/K1ABC'
     print*,'          hashcodes YW18FIFA'
     go to 999
  endif
  call getarg(1,callsign)
  callsign=adjustl(callsign)

  do k=1,3
     n8(k)=0
     do i=1,11
        j=index(c,callsign(i:i)) - 1
        n8(k)=38*n8(k) + j
     enddo
     ihash(k)=ishft(nprime*n8(k),nbits(k)-64)
  enddo
  ih22_biased=ihash(3) + NTOKENS
  write(*,1000) callsign,ihash,ih22_biased
1000 format('Callsign',9x,'h10',7x,'h12',7x,'h22'/41('-')/        &
          a11,i9,2i10,/'Biased for storage in c28:',i14)

999 end program hashcodes
"""


def main():
    NTOKENS = 2063592
    c = " 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ/"
    nprime = 47055833459
    nbits = [10, 12, 22]

    if len(sys.argv) != 2:
        print("Usage:    hashcodes <callsign>")
        print("Examples: hashcodes PJ4/K1ABC")
        print("          hashcodes YW18FIFA")
        return

    # Get callsign and left-justify (equivalent to Fortran's adjustl)
    callsign = sys.argv[1].lstrip().ljust(11)

    n8 = [0, 0, 0]
    ihash = [0, 0, 0]

    for k in range(3):
        for i in range(11):
            # Find index in character set (equivalent to Fortran's index() - 1)
            j = c.find(callsign[i]) if i < len(callsign) else 0
            n8[k] = 38 * n8[k] + j

        # Calculate hash
        # Equivalent to Fortran's ishft(nprime*n8(k), nbits(k)-64)
        # For 64-bit arithmetic with right shift
        product = (nprime * n8[k]) & ((1 << 64) - 1)  # 64-bit mask
        ihash[k] = (product >> (64 - nbits[k])) & ((1 << nbits[k]) - 1)

    ih22_biased = ihash[2] + NTOKENS

    print("Callsign        h10       h12       h22")
    print("-" * 41)
    print(f"{callsign:<11}{ihash[0]:9}{ihash[1]:10}{ihash[2]:10}")
    print(f"Biased for storage in c28:{ih22_biased:14}")


if __name__ == "__main__":
    main()
