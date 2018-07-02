#define  PHYSICS                        MHD
#define  DIMENSIONS                     3
#define  COMPONENTS                     3
#define  GEOMETRY                       CARTESIAN
#define  BODY_FORCE                     VECTOR
#define  FORCED_TURB                    NO
#define  COOLING                        NO
#define  RECONSTRUCTION                 WENO3
#define  TIME_STEPPING                  RK3
#define  DIMENSIONAL_SPLITTING          NO
#define  NTRACER                        0
#define  USER_DEF_PARAMETERS            2

/* -- physics dependent declarations -- */

#define  EOS                            IDEAL
#define  ENTROPY_SWITCH                 NO
#define  DIVB_CONTROL                   CONSTRAINED_TRANSPORT
#define  BACKGROUND_FIELD               NO
#define  AMBIPOLAR_DIFFUSION            NO
#define  RESISTIVITY                    NO
#define  HALL_MHD                       NO
#define  THERMAL_CONDUCTION             NO
#define  VISCOSITY                      NO
#define  ROTATING_FRAME                 NO

/* -- user-defined parameters (labels) -- */

#define  BETA                           0
#define  CSOUND                         1

/* [Beg] user-defined constants (do not change this line) */

#define  CHAR_LIMITING                  YES
#define  CT_EMF_AVERAGE                 UCT_CONTACT
#define  NET_FLUX                       YES
#define  STRATIFICATION                 NO
#define  CHECK_DIVB_CONDITION           TRUE

/* [End] user-defined constants (do not change this line) */
