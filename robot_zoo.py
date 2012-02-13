#!/usr/bin/python2.7 -B

import twitter
import pycron

import casio_f91w as _casio_f91w             
import deoldehove as _deoldehove            
import msvlieland as _msvlieland
import hetluchtalarm as _hetluchtalarm
import convertbot as _convertbot
import grotebroer1 as _grotebroer1

def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--quiet', action='store_true', default=False, help='only output errors')
    parser.add_argument('-d', '--debug', action='store_true', default=False, help='output everything')
    return parser.parse_args()
   
args = parse_args()

if args.quiet: twitter.LoggingObject.LEVEL = twitter.LoggingObject.LEVEL_ERROR 
if args.debug: twitter.LoggingObject.LEVEL = twitter.LoggingObject.LEVEL_DEBUG

casio_f91w = _casio_f91w.CasioF91W('casio_f91w')
deoldehove = _deoldehove.DeOldehove('deoldehove')
msvlieland = _msvlieland.MsVlieland('msvlieland')
hetluchtalarm = _hetluchtalarm.Luchtalarm('hetluchtalarm')
convertbot = _convertbot.ConvertBot('convertbot')
grotebroer1 = _grotebroer1.GroteBroer1('grotebroer1')

cron = pycron.CronRunner(
    #   -------- -------- -------- -------- -------- -------- --------
    #   second   minute   hour     monthday month    year     weekday
    #   -------- -------- -------- -------- -------- -------- --------

    #                                                                   @casio_f91w
      ('*        00       *        *        *        *        *       ', casio_f91w.send_beep)
    , ('05-59/30 *        *        *        *        *        *       ', casio_f91w.handle_mentions)

    #                                                                   @deoldehove
    , ('*        00-59/30 *        10-12    sep      2010     *       ', deoldehove.sound_clock_lwd_culinair)
    , ('*        00-59/30 *        09-11    sep      2011     *       ', deoldehove.sound_clock_lwd_culinair)
    , ('*        00-59/30 *        07-09    sep      2012     *       ', deoldehove.sound_clock_lwd_culinair)

    , ('*        00-59/30 09-23    13       aug      2011     *       ', deoldehove.sound_clock_into_the_grave)
    , ('*        00-59/30 00-08    14       aug      2011     *       ', deoldehove.sound_clock_into_the_grave)

    , ('*        00-59/30 09-23    11       aug      2012     *       ', deoldehove.sound_clock_into_the_grave)
    , ('*        00-59/30 00-08    12       aug      2012     *       ', deoldehove.sound_clock_into_the_grave)

    , ('*        00-59/30 *        *        *        *        *       ', deoldehove.sound_clock)

    #                                                                   @msvlieland
    , ('*        15       10       04-15    feb      2012     *       ', msvlieland.sound_horn)
    , ('*        30       15       04-15    feb      2012     *       ', msvlieland.sound_horn)

    , ('*        00       09       04-15    feb      2012     *       ', msvlieland.geen_afvaart)
    , ('*        00       09       *        *        *        *       ', msvlieland.sound_horn)

    , ('*        15       14       04-15    feb      2012     *       ', msvlieland.geen_afvaart)
    , ('*        15       14       *        *        *        *       ', msvlieland.sound_horn)

    , ('*        00       19       04-15    feb      2012     *       ', msvlieland.geen_afvaart)
    , ('*        00       19       *        *        *        *       ', msvlieland.sound_horn)

    #                                                                   @convertbot
    , ('00       *        *        *        *        *        *       ', convertbot.post_time)

    #                                                                   @hetluchtalarm
    , ('*        00       12       01-07    *        *        mon     ', hetluchtalarm.sound_alarm)

    #                                                                   @grotebroer1
    , ('00-59/15 *        *        *        *        *        *       ', grotebroer1.check_dm)
    , ('00-59/20 *        *        *        *        *        *       ', grotebroer1.search_firehose)
    , ('05       *        *        *        *        *        *       ', grotebroer1.follow_suspects)

    #   -------- -------- -------- -------- -------- -------- --------
)

casio_f91w.check()
deoldehove.check()
msvlieland.check()
hetluchtalarm.check()
convertbot.check()
grotebroer1.check()

try:
    grotebroer1.start_firehose()
    cron.start_executor()
    cron.run_local()
except KeyboardInterrupt:
    cron.log('Exiting')
finally:
    cron.stop_executor()
    grotebroer1.stop_firehose()

