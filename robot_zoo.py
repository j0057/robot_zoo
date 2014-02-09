#!/usr/bin/env python

import time
import threading
import logging

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
from bot import geotweets as _geotweets
from bot import johndoeveloper as _johndoeveloper

def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--quiet', action='store_true', default=False, help='only output errors')
    parser.add_argument('-d', '--debug', action='store_true', default=False, help='output everything')
    return parser.parse_args()
   
class RobotZooCET(pycron.CronRunner):
    def __init__(self, name, executor):
        super(RobotZooCET, self).__init__(name, time.localtime, executor,
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
            , ('00       00       00       *        *        *        *       ', msvlieland.update_departures)
            , ('00       59       08       *        *        *        *       ', msvlieland.update_departures_for_today)
            , ('00       *        *        *        *        *        *       ', msvlieland.sound_horn_dynamic)

            #   ........ ........ ........ ........ ........ ........ ........  @convertbot
            , ('00       *        *        *        *        *        *       ', convertbot.post_time)

            #   ........ ........ ........ ........ ........ ........ ........  @hetluchtalarm
            , ('*        00       12       01       04       2013     *       ', hetluchtalarm.tweede_paasdag_2013)
            , ('*        00       12       01-07    *        *        mon     ', hetluchtalarm.sound_alarm)

            #   ........ ........ ........ ........ ........ ........ ........  @maanfase
            , ('00       *        *        *        *        *        *       ', maanfase.post_phase)

            #   ........ ........ ........ ........ ........ ........ ........  @grotebroer1
            , ('01-59/15 *        *        *        *        *        *       ', grotebroer1.update_regex)

            #   ........ ........ ........ ........ ........ ........ ........  geotweets
            , ('05       *        *        *        *        *        *       ', geotweets.save_raw)
            , ('04       *        *        *        *        *        *       ', geotweets.create_viz)

            #   -------- -------- -------- -------- -------- -------- --------
        )

class RobotZooUTC(pycron.CronRunner):
    def __init__(self, name, executor):
        super(RobotZooUTC, self).__init__(name, time.gmtime, executor,
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


if __name__ == '__main__':

    args = parse_args()

    logging.basicConfig(level=(logging.DEBUG if args.debug else
                               logging.ERROR if args.quiet else logging.INFO),
                        format='%(asctime)s %(name)s - %(threadName)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    if not args.debug:
        logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.ERROR)

    if args.quiet: twitter.LoggingObject.LEVEL = twitter.LoggingObject.LEVEL_ERROR 
    if args.debug: twitter.LoggingObject.LEVEL = twitter.LoggingObject.LEVEL_DEBUG

    logging.info('Robot zoo starting')

    casio_f91w = _casio_f91w.CasioF91W('casio_f91w')
    deoldehove = _deoldehove.DeOldehove('deoldehove')
    msvlieland = _msvlieland.MsVlieland('msvlieland')
    hetluchtalarm = _hetluchtalarm.Luchtalarm('hetluchtalarm')
    convertbot = _convertbot.ConvertBot('convertbot')
    grotebroer1 = _grotebroer1.GroteBroer1('grotebroer1')
    y2k38warning = _y2k38warning.Y2K38Warning('y2k38warning')
    maanfase = _maanfase.Maanfase('maanfase')
    geotweets = _geotweets.GeoTweets('johndoeveloper')
    firehose = _johndoeveloper.Firehose('johndoeveloper', '3.23,50.75,7.23,53.75')

    executor = pycron.CronExecutor()
    cron_cet = RobotZooCET('cron_cet', executor.queue)
    cron_utc = RobotZooUTC('cron_utc', executor.queue)

    casio_f91w.api.check()
    deoldehove.api.check()
    msvlieland.api.check()
    hetluchtalarm.api.check()
    convertbot.api.check()
    grotebroer1.api.check()
    y2k38warning.api.check()
    maanfase.api.check()
    geotweets.api.check()
    firehose.api.check()

    firehose.add_listener(grotebroer1.inspector)
    firehose.add_listener(geotweets)

    cancel = [ cron_cet.run(),
               cron_utc.run(),
               executor.run(count=4),
               grotebroer1.userstream.run(),
               grotebroer1.inspector.run(),
               geotweets.process(),
               firehose.run() ]
    try:
        while True: 
            time.sleep(1)
    except KeyboardInterrupt:
        print
        logging.info('Main thread got keyboard interrupt')
    finally:
        map(lambda cancel: cancel(), cancel)

