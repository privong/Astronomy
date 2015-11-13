/* lmst.c
 *
 * Compute and return the LMST, based on the current time and an input
 * longitude.
 *
 * Equations from:
 * https://www.cv.nrao.edu/~rfisher/Ephemerides/times.html
 *
 * George C. Privon
 *
 * Compile with:
 *  gcc lmst.c -o lmst -lm
 *
 * Usage:
 *  lmst longitude [date time]
 *
 * Where longitude is in decimal degrees with E long positive and W long negative.
 * [date time] is option and must be given in the computer's timezone and be in
 *  the format YYYY-MM-DDTHH:MM
 */

#define _XOPEN_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>

int main(int argc, char **argv) {

    time_t obstime;
    char obstimestr[40];
    struct tm obstimestruct;
    double d, t, GMST_s, LMST_s;
    int hour, min, sec;
    float lon;

    if (argc == 2) {    /* assume we just want current LMST */
        lon = atof(argv[1]);
        obstime = time(NULL);   /* seconds since Unix epoch */
    } else if (argc == 3) { /* LMST at a specified day+time */
        lon = atof(argv[1]);
        strptime(argv[2], "%Y-%m-%dT%H:%M", &obstimestruct);
        strftime(obstimestr, 40, "%s", &obstimestruct);
        obstime = atof(obstimestr);
    } else {
        fprintf(stderr, "Error: Incorrect usage.\n\n");
        fprintf(stderr, "Usage:\n");
        fprintf(stderr, "%s longitude [date time]\n\n", argv[0]);
        fprintf(stderr, "Where longitude is in degrees and E is positive.\n");
        fprintf(stderr, "[date time] is optional and should be in the computer's time zone and in the format YYYY-MM-DDTHH:MM\n");
        return -1;
    }

    /* add JD to get to the UNIX epoch, then subtract to get the days since
     * 2000 Jan 01, 12h UT1 */
    d = (obstime / 86400.0) + 2440587.5 - 2451545.0;
    t = d / 36525;

    GMST_s = 24110.54841 + 8640184.812866 * t + 0.093104 * pow(t, 2) - 0.0000062 * pow(t, 3);
    /* convert from UT1=0 */
    GMST_s += obstime;
    GMST_s = GMST_s - 86400.0 * floor(GMST_s / 86400.0);

    /* adjust to LMST */
    LMST_s = GMST_s + 3600*lon/15.;
    
    if (LMST_s <= 0) {  /* LMST is between 0 and 24h */
        LMST_s += 86400.0;
    }
    
    hour = floor(LMST_s / 3600.);
    LMST_s -= 3600. * floor(LMST_s / 3600);
    min = floor(LMST_s / 60.);
    sec = LMST_s - 60 * floor(LMST_s / 60.);

    printf("%02d:%02d:%02d\n", hour, min, sec);

return 0;
}
