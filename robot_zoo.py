#!/usr/bin/env python

import time

import twitter
import pycron

from bot import casio_f91w as _casio_f91w             
from bot import deoldehove as _deoldehove            
from bot import msvlieland as _msvlieland
from bot import hetluchtalarm as _hetluchtalarm
from bot import convertbot as _convertbot
from bot import grotebroer1 as _grotebroer1
from bot import y2k38warning as _y2k38warning
from bot import maanfase as _maanfase

def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--quiet', action='store_true', default=False, help='only output errors')
    parser.add_argument('-d', '--debug', action='store_true', default=False, help='output everything')
    return parser.parse_args()
   
class RobotZooCET(pycron.CronRunner):
    def __init__(self, name, executor):
        super(RobotZooCET, self).__init__(name, executor,
            #   -------- -------- -------- -------- -------- -------- --------
            #   second   minute   hour     monthday month    year     weekday
            #   -------- -------- -------- -------- -------- -------- --------

            #   ........ ........ ........ ........ ........ ........ ......... @casio_f91w
              ('*        00       *        *        *        *        *       ', casio_f91w.send_beep)
            , ('01       00-59/02 *        *        *        *        *       ', casio_f91w.handle_mentions)
            , ('02       *        *        *        *        *        *       ', casio_f91w.send_alarms)

            #   ........ ........ ........ ........ ........ ........ ........  @deoldehove
            , ('*        00-59/30 *        10-12    sep      2010     *       ', deoldehove.sound_clock_lwd_culinair)
            , ('*        00-59/30 *        09-11    sep      2011     *       ', deoldehove.sound_clock_lwd_culinair)
            , ('*        00-59/30 *        07-09    sep      2012     *       ', deoldehove.sound_clock_lwd_culinair)

            , ('*        00-59/30 09-23    13       aug      2011     *       ', deoldehove.sound_clock_into_the_grave)
            , ('*        00-59/30 00-08    14       aug      2011     *       ', deoldehove.sound_clock_into_the_grave)

            , ('*        00-59/30 09-23    11       aug      2012     *       ', deoldehove.sound_clock_into_the_grave)
            , ('*        00-59/30 00-08    12       aug      2012     *       ', deoldehove.sound_clock_into_the_grave)

            , ('*        00-59/30 09-23    10       aug      2013     *       ', deoldehove.sound_clock_into_the_grave)
            , ('*        00-59/30 00-08    11       aug      2013     *       ', deoldehove.sound_clock_into_the_grave)

            , ('*        00-59/30 *        *        *        *        *       ', deoldehove.sound_clock)

            #   ........ ........ ........ ........ ........ ........ ........  @msvlieland
            , ('*        15       10       04-16    feb      2012     *       ', msvlieland.sound_horn) # ijs op waddenzee 2012 
            , ('*        30       15       04-16    feb      2012     *       ', msvlieland.sound_horn)

            , ('*        00       09       17       feb      2012     *       ', msvlieland.sound_horn)
            , ('*        00       17       17       feb      2012     *       ', msvlieland.sound_horn)

            , ('*        00       09       04-17    feb      2012     *       ', msvlieland._)
            , ('*        15       14       04-17    feb      2012     *       ', msvlieland._)
            , ('*        00       19       04-17    feb      2012     *       ', msvlieland._)

            , ('*        00       09       *        apr-sep  2012     *       ', msvlieland.sound_horn) # zomerdienstregeling 2012
            , ('*        15       14       *        apr-sep  2012     *       ', msvlieland.sound_horn)
            , ('*        00       19       *        apr-sep  2012     *       ', msvlieland.sound_horn)

            , ('*        00       09       25       dec      2012     *       ', msvlieland._) # winterdienstregeling 2012
            , ('*        00       09       *        oct-dec  2012     sun     ', msvlieland._)
            , ('*        00       09       *        oct-dec  2012     *       ', msvlieland.sound_horn)
            
            , ('*        00       09       01       04       2013     mon     ', msvlieland._) # dienstregeling 2013: 9:00
            , ('*        00       09       *        *        2013     mon     ', msvlieland.sound_horn)
            , ('*        00       09       01       01       2013     tue     ', msvlieland._)
            , ('*        00       09       *        *        2013     tue     ', msvlieland.sound_horn)
            , ('*        00       09       25       12       2013     wed     ', msvlieland._)
            , ('*        00       09       *        *        2013     wed     ', msvlieland.sound_horn)
            , ('*        00       09       *        *        2013     thu     ', msvlieland.sound_horn)
            , ('*        00       09       *        *        2013     fri     ', msvlieland.sound_horn)
            , ('*        00       09       *        *        2013     sat     ', msvlieland.sound_horn)
            , ('*        00       09       *        01-03    2013     sun     ', msvlieland._)
            , ('*        00       09       01-19    04       2013     sun     ', msvlieland._)
            , ('*        00       09       *        10-12    2013     sun     ', msvlieland._)
            , ('*        00       09       *        *        2013     sun     ', msvlieland.sound_horn)

            , ('*        15       14       *        *        2013     *       ', msvlieland.sound_horn) # dienstregeling 2013: 14:15

            , ('*        00       19       *        01-03    2013     mon     ', msvlieland._) # dienstregeling 2013: 19:00
            , ('*        00       19       02-19    04       2013     mon     ', msvlieland._)
            , ('*        00       19       *        10-12    2013     mon     ', msvlieland._)
            , ('*        00       19       *        *        2013     mon     ', msvlieland.sound_horn)
            , ('*        00       19       24       12       2013     tue     ', msvlieland._)
            , ('*        00       19       31       12       2013     tue     ', msvlieland._)
            , ('*        00       19       *        *        2013     tue     ', msvlieland.sound_horn)
            , ('*        00       19       *        01-03    2013     wed     ', msvlieland._)
            , ('*        00       19       01-19    04       2013     wed     ', msvlieland._)
            , ('*        00       19       *        10-12    2013     wed     ', msvlieland._)
            , ('*        00       19       *        *        2013     wed     ', msvlieland.sound_horn)
            , ('*        00       19       28       03       2013     thu     ', msvlieland._)
            , ('*        00       19       *        01-03    2013     thu     ', msvlieland._)
            , ('*        00       19       01-19    04       2013     thu     ', msvlieland._)
            , ('*        00       19       *        10-12    2013     thu     ', msvlieland._)
            , ('*        00       19       *        *        2013     thu     ', msvlieland.sound_horn)
            , ('*        00       19       *        *        2013     fri     ', msvlieland.sound_horn)
            , ('*        00       19       *        01-03    2013     sat     ', msvlieland._)
            , ('*        00       19       01-19    04       2013     sat     ', msvlieland._)
            , ('*        00       19       *        10-12    2013     sat     ', msvlieland._)
            , ('*        00       19       *        *        2013     sat     ', msvlieland.sound_horn)
            , ('*        00       19       *        *        2013     sun     ', msvlieland.sound_horn)

            #   ........ ........ ........ ........ ........ ........ ........  @convertbot
            , ('00       *        *        *        *        *        *       ', convertbot.post_time)

            #   ........ ........ ........ ........ ........ ........ ........  @hetluchtalarm
            , ('*        00       12       01       04       2013     *       ', hetluchtalarm.tweede_paasdag_2013)
            , ('*        00       12       01-07    *        *        mon     ', hetluchtalarm.sound_alarm)

            #   ........ ........ ........ ........ ........ ........ ........  @maanfase
            , ('00       *        *        *        *        *        *       ', maanfase.post_phase)

            #   ........ ........ ........ ........ ........ ........ ........  @grotebroer1
            , ('00-59/15 *        *        *        *        *        *       ', grotebroer1.firehose.firehose_update)

            #   -------- -------- -------- -------- -------- -------- --------
        )

class RobotZooUTC(pycron.CronRunner):
    def __init__(self, name, executor):
        super(RobotZooUTC, self).__init__(name, executor,
            #   -------- -------- -------- -------- -------- --------- --------
            #   second   minute   hour     monthday month    year      weekday
            #   -------- -------- -------- -------- -------- --------- --------

            #   ........ ........ ........ ........ ........ ......... ........  @y2k38warning (2038-01-19 03:14:07)
              ('07       14       03       19       01       2013-2036 *       ', y2k38warning.yearly) 
            , ('07       14       03       19       01-11    2037      *       ', y2k38warning.monthly)
            , ('07       14       03       19-31    12       2037      *       ', y2k38warning.daily)
            , ('07       14       03       01-17    01       2038      *       ', y2k38warning.daily)
            , ('07       14       03-23    18       01       2038      *       ', y2k38warning.hourly)
            , ('07       14       00-01    19       01       2038      *       ', y2k38warning.hourly)
            , ('07       14-59    02       19       01       2038      *       ', y2k38warning.every_minute)
            , ('07       00-13    03       19       01       2038      *       ', y2k38warning.every_minute)
            , ('07-59    13       03       19       01       2038      *       ', y2k38warning.every_second)
            , ('00-06    14       03       19       01       2038      *       ', y2k38warning.every_second)
            , ('07       14       03       19       01       2038      *       ', y2k38warning.zero)
            #   -------- -------- -------- -------- -------- --------- --------
        )


casio_f91w = _casio_f91w.CasioF91W('casio_f91w')
deoldehove = _deoldehove.DeOldehove('deoldehove')
msvlieland = _msvlieland.MsVlieland('msvlieland')
hetluchtalarm = _hetluchtalarm.Luchtalarm('hetluchtalarm')
convertbot = _convertbot.ConvertBot('convertbot')
grotebroer1 = _grotebroer1.GroteBroer1('grotebroer1')
y2k38warning = _y2k38warning.Y2K38Warning('y2k38warning')
maanfase = _maanfase.Maanfase('maanfase')

if __name__ == '__main__':

    args = parse_args()

    if args.quiet: twitter.LoggingObject.LEVEL = twitter.LoggingObject.LEVEL_ERROR 
    if args.debug: twitter.LoggingObject.LEVEL = twitter.LoggingObject.LEVEL_DEBUG

    cron_executor = pycron.CronExecutor(pool_size=4)

    cron_cet = RobotZooCET('cron_cet', cron_executor)
    cron_utc = RobotZooUTC('cron_utc', cron_executor)

    casio_f91w.api.check()
    deoldehove.api.check()
    msvlieland.api.check()
    hetluchtalarm.api.check()
    convertbot.api.check()
    grotebroer1.api.check()
    y2k38warning.api.check()
    maanfase.api.check()

    try:
        grotebroer1.firehose.firehose_start()
        grotebroer1.userstream.userstream_start()
        cron_executor.start()
        cron_cet.start_local()
        cron_utc.start_utc()
        while True: 
            time.sleep(5)
    except KeyboardInterrupt:
        print
        cron_executor.log('Main thread got keyboard interrupt')
    finally:
        cron_executor.stop()
        cron_cet.stop()
        cron_utc.stop()
        grotebroer1.userstream.userstream_stop()
        grotebroer1.firehose.firehose_stop()
