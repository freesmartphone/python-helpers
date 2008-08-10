/* pyrtc low level functions
   Authored by Michael 'Mickey' Lauer <mlauer@vanille-media.de>
   (C) 2008 OpenMoko, Inc.
   LGPLv3
*/

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <time.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/rtc.h>

#define DEFAULT_RTC "/dev/rtc0"

static const char *device = DEFAULT_RTC;

static int rtc_read_time(struct rtc_time* tm)
{
    int fd = open(device, O_RDONLY);
    if (fd < 0) {
        perror(device);
        return 0;
    }

    int res = ioctl(fd, RTC_RD_TIME, tm);
    if (res < 0) {
        perror("ioctl(RTC_RD_TIME)");
        close(fd);
        return 0;
    }

    close(fd);
    return 1;
}

static int rtc_write_time(struct rtc_time* tm)
{
    int fd = open(device, O_RDONLY);
    if (fd < 0) {
        perror(device);
        return 0;
    }

    int res = ioctl(fd, RTC_SET_TIME, tm);
    if (res < 0) {
        perror("ioctl(RTC_SET_TIME)");
        close(fd);
        return 0;
    }

    close(fd);
    return 1;
}

static int rtc_read_alarm(struct rtc_wkalrm* alarm)
{
    int fd = open(device, O_RDONLY);
    if (fd < 0) {
        perror(device);
        return 0;
    }

    int res = ioctl(fd, RTC_WKALM_RD, alarm);
    if (res < 0) {
        perror("ioctl(RTC_WKALM_RD)");
        close(fd);
        return 0;
    }

    close(fd);
    return 1;
}

static int rtc_write_alarm(struct rtc_wkalrm* alarm)
{
    int fd = open(device, O_RDONLY);
    if (fd < 0) {
        perror(device);
        return 0;
    }

    int res = ioctl(fd, RTC_WKALM_SET, alarm);
    if (res < 0) {
        perror("ioctl(RTC_WKALM_SET)");
        close(fd);
        return 0;
    }

    close(fd);
    return 1;
}

static int rtc_disable_alarm()
{
    struct rtc_wkalrm alarm;

    if ( !rtc_read_alarm(&alarm) )
        return 0;
    alarm.enabled = 0;
    return rtc_write_alarm(&alarm);
}
