#!/usr/bin/python

#ライブラリのインクルードパスを追加
import sys
sys.path.append("/usr/local/lib/python2.7/site-packages")

import time
import ouimeaux
from ouimeaux.environment import Environment
from daemon import daemon
from daemon.pidlockfile import PIDLockFile


def wemo_main():
    print "Start WEMO Daemon."

    print "Set Environment."
    #キャッシュを参照しようとすると動作が激重orストップするので参照しない
    wemo = Environment(with_cache=False)
    print "Finished init Environment."

    print "Starting WEMO module."
    wemo.start()
    print "Finished."

    print "Discovering..."
    wemo.discover(5)
    print "Finished discovering."

    print "Get Switch Instances."
    east = wemo.get_switch("Lab East")
    west = wemo.get_switch("Lab West")
    heater = wemo.get_switch("Lab Heater")
    print "Finished."

    print "Set GPIO pins."
    open("/sys/class/gpio/export", "w").write(str(44))
    open("/sys/class/gpio/export", "w").write(str(19))
    open("/sys/class/gpio/export", "w").write(str(110))

    print "All init is finished."

    print "Start Loop."
    while True:
        if int(open("/sys/class/gpio/gpio44/value", "r").read().split("\n")[0]) == 0:
            #左ボタンが押された時の処理
            print "east toggle"
            east.toggle()
            print "waiting..."
            #チャタリングと長押し対策
            time.sleep(0.5)
            continue
        if int(open("/sys/class/gpio/gpio19/value", "r").read().split("\n")[0]) == 0:
            #中央ボタンが押された時の処理
            print "west toggle"
            west.toggle()
            print "waiting..."
            #チャタリングと長押し対策
            time.sleep(0.5)
            continue
        if int(open("/sys/class/gpio/gpio110/value", "r").read().split("\n")[0]) == 0:
            #右ボタンが押された時の処理
            print "heater toggle"
            heater.toggle()
            print "waiting..."
            #チャタリングと長押し対策
            time.sleep(0.5)
            continue
        print "nothing loop"
        time.sleep(0.2)

#スクリプトとして動作された場合、ここから実行される
if __name__ == '__main__':
    #daemonとして動作する場合の処理
    #pidファイルは/etc/init.d/wemo内の指定と同じファイルにする
    with daemon.DaemonContext(pidfile=PIDLockFile('/var/run/wemo.pid')):
        #daemonとして起動した際に、networking側の処理が追いつかずにネットワークが確立していない場合がある。
        #その場合Environment()などでexceptionを吐いて終了してしまう。
        #対応として、exceptで全部のexceptionを受け止めてもう一度wemo_main()をやり直すようにした。
        while True:
            try:
                wemo_main()
            except:
                time.sleep(3)
