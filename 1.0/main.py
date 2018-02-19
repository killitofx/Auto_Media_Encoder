import os, time, shutil, subprocess, json

check_time = del_origi_file = support_media = environment = ''
finish_locate = check_locate = original_locate =work_locate = compare = compare_data = ruler = ''
method = 0
homedir = os.getcwd()
config = 'config.data'
log = 'log.txt'
support_list = []
finish_diary = homedir + '\\' + 'finish'
# finish_diary = r'\\192.168.10.9\video'
origi_diary = homedir + '\\' + 'original'
def read_cfg(data):
    with open(config, 'r') as f:
        line = f.readline()
        while line:
            if not '#'in line:
                if data in line:
                    line = line.replace('\n','')
                    #line = line.strip('\n')
                    cfg = line.split(':', 1)[-1]
                    return cfg
            line = f.readline()

class check(object):
    def __init__(self):
        self.check_config()
        self.support_list_add()
        self.check_diary()
    def check_config(self):
        if not os.path.exists(config):
            print("没有找到配置文件...")
            self.write_config()
        else:
            print("配置文件已找到")
            self.read_config()

    def read_config(self):
        global check_time, del_origi_file, support_media, environment,finish_diary,origi_diary,work_locate,ruler,compare,compare_data
        check_time= read_cfg('check_time')
        del_origi_file = read_cfg('del_origi_file')
        environment = read_cfg('environment_variable')
        support_media = read_cfg('support_media')
        finish_diary = read_cfg('finish_locate')
        origi_diary = read_cfg('original_locate')
        work_locate = read_cfg('check_locate')
        ruler = read_cfg('ruler')
        compare = read_cfg('compare')
        compare_data = read_cfg('compare_data')
        if 'k' in compare_data:
            compare_data = int(compare_data[:-1])
        try:
            compare_data = int(compare_data)*1000
        except:
            print("请检查规则是否正确")
            time.sleep(3)
            exit()




    def support_list_add(self):
        global support_media,support_list
        for line in support_media.split(','):
            #line = line.strip('\n')
            #print(line)
            support_list.append(line)
        # try:
        #     support_list.remove('\n')
        # except:
        #     print("检查support_list最后是否少逗号")

    def check_diary(self):
        err_flg = 0
        check1 = os.path.exists(finish_diary)
        if check1:
            print("finish文件夹已找到")
        else:
            print("未发现finish文件夹，创建...")
            try:
                os.makedirs(finish_diary)
                print("创建成功")
            except:
                print("创建失败，请检查权限")
                err_flg = 1

        check2 = os.path.exists(work_locate)
        if check2:
            print("工作文件夹已找到")
        else:
            print("未发现工作文件夹，创建...")
            try:
                os.makedirs(work_locate)
                print("创建成功")
            except:
                print("创建失败，请检查权限")
                err_flg = 1

        if '0' in del_origi_file:
            check2 = os.path.exists(origi_diary)
            if check2:
                print("original文件夹已找到")
            else:
                print("未发现original文件夹，创建。。。")
                try:
                    os.makedirs(origi_diary)
                    print("创建成功")
                except:
                    print("创建失败，请检查权限")
                    err_flg = 1
        if err_flg:
            time.sleep(3)
            exit()


    def write_config(self):
        print('正在创建配置文件...')
        with open(config,'w') as f:
            f.write('#修改后请重启exe\n#若del_origi_file为1，则删除源文件，反之保留\ndel_origi_file:1\n\ncheck_time:30\n\nenvironment_variable:0\n\nsupport_media:mkv,flv,rmvb\n\n')
            f.write('finish_locate:%s\n\ncheck_locate:%s\n\noriginal_locate:%s\n\nruler:0\n\ncompare:>\n\ncompare_data:1500k\n\n' % (finish_diary, homedir, origi_diary))
            f.write('mkv:ffmpeg -i data1 -c:v copy -c:a copy data2\nmkv1:ffmpeg -i data1 -c:v copy -c:a copy data2\n\n')
            f.write('flv:ffmpeg -i data1 -y -vcodec copy -acodec copy data2\nflv1:ffmpeg -i data1 -y -vcodec copy -acodec copy data2\n\n')
            f.write('rmvb:ffmpeg -i data1 -acodec copy -vcodec libx264 -b 1500k  -f mp4 data2\nrmvb1:ffmpeg -i data1 -acodec copy -vcodec libx264 -b 1500k  -f mp4 data2\n\n')
        print("配置文件以生成，检查后重启本程序...")
        time.sleep(2)
        exit()

class ffmpeg(object):
    def __init__(self):
        self.worklist = []
        self.check_new_file()
        if self.worklist == []:
            print("没有文件需要被转码\n")
            #self.add_log("没有文件需要被转码")
        else:
            self.check_name()


    def check_new_file(self):
        for i in os.listdir(work_locate):
            for k in support_list:
                if k in i:
                    self.worklist.append(i)
        print('转码队列', self.worklist)

    def check_name(self):
        for i in self.worklist:
            self.file = i
            self.tag = i.split('.')[-1]
            self.name = i.split('.')[-2]
            cmd = self.find_config(self.tag, i)
            self.add_log("文件%s开始转码" % i)
            print("文件%s开始转码" % i)
            # self.add_log("转码参数%s" % cmd)
            # print(cmd)
            self.ffmpeg(cmd)

    def find_config(self, tag, file_name):
        global environment
        if 'bit_rate' or 'size' in ruler:
            self.add_log('筛选器启动,规则：%s' % ruler)
            print("筛选器启动,规则：%s" % ruler)
            if ffprobe(work_locate+'\\'+self.file, 'format', ruler, compare, compare_data):
                self.x = '1'
                self.add_log('使用备用参数')
                print('使用备用参数')
            else:
                self.add_log('使用主参数')
                print('使用主参数')
        else:
            self.x = ''
            self.add_log('筛选器关闭，使用主参数')
            print('筛选器关闭，使用主参数')

        if '0' in environment:
            cfg = read_cfg(tag + self.x + ':')
            # print(tag + self.x + ':')
            cfg = cfg.replace('data1', work_locate + '\\' + file_name, 1)
            cfg = cfg.replace('data2', finish_diary + '\\' + self.name + '.mp4')
            cfg = cfg.replace('ffmpeg', homedir + '\\ffmpeg.exe', 1)
        else:
            cfg = read_cfg(tag + self.x + ':')
            cfg = cfg.replace('data1', file_name, 1)
            cfg = cfg.replace('data2', 'finish' + '\\' + self.name + '.mp4')
        self.add_log("转码参数%s" % cfg)
        return cfg

    def ffmpeg(self, cmd):
        returnCode = subprocess.call(cmd, shell=True, stdin=subprocess.PIPE)
        #print('returncode:', returnCode)
        if not returnCode:
            print(self.file, "转码成功")
            self.add_log("文件%s转码成功" % self.file)
            self.move_file()
        else:
            print(self.file, "转码失败")
            self.add_log("文件%s转码失败" % self.file)

    def move_file(self):
        if '0' in del_origi_file:
            shutil.move(work_locate + '\\' + self.file, origi_diary+'\\'+self.file)
            print("源文件已归档")
            self.add_log("文件%s源文件已归档\n\n" % self.file)
        elif '1' in del_origi_file:
            os.remove(work_locate + '\\' + self.file)
            print("源文件已删除")
            self.add_log("文件%s源文件已删除\n\n" % self.file)

    def add_log(self, data):
        with open(log, 'a') as f:
            f.write(time.asctime(time.localtime(time.time())) + '  '+data+'\n')

class ffprobe(object):
    def __init__(self, file, list1 ,list2 ,compare, compare_data):
        self.file = file
        self.list1 = list1
        self.list2 = list2
        self.compare = compare
        self.compare_data = compare_data
        self.run_ffprobe()
        self.check_bitrate()

    def run_ffprobe(self):
        strCmd = homedir+'\\'+'ffprobe.exe -v quiet -print_format json -show_format -show_streams -i "' + self.file + '"'
        data = os.popen(strCmd).read()
        data = (json.loads(data))
        # print(data)
        data = data['format'][self.list2]
        self.data = int(data)


    def check_bitrate(self):
        global method
        if '>' in self.compare:
            if self.data > self.compare_data:
                method = 1
                return 1
            else:
                method = 0
                return 0
        elif '<' in self.compare:
            if self.data < self.compare_data:
                method = 1
                return 1
            else:
                method = 0
                return 0



def main():
    check()
    #time_value = int((check_time.replace('\n','')).split('=')[-1])
    time_value = (int(check_time))
    flag = 0
    try:
        if flag<10:
            while True:
                ffmpeg()
                time.sleep(time_value)
        else:
            exit()
    except:
        print("发生了未知的错误，如再次发生，请联系开发者")
        time.sleep(10)
        flag += 1
        main()


if __name__=='__main__':
    main()
# check()
# ffmpeg()
