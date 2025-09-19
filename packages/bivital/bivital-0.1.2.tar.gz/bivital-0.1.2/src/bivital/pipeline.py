
import os
import configparser
from datetime import datetime
import tkinter
from tkinter.filedialog import askdirectory, askopenfilename 
import shutil
import time
import serial
import errno
import warnings
import csv
from importlib.resources import files
import subprocess
import tempfile
warnings.filterwarnings('ignore')


class BiVital_DataPipeline:

    def create_config(self,config_path, project_name):
        config = configparser.ConfigParser()

        # Add sections and key-value pairs
        config['General'] = {'BiVital_Data' : False}
        config['Database'] = {'p_name': project_name}

        # Write the configuration to a file
        config_name = "config.ini"
        config_path = os.path.join(config_path,config_name)
        with open(config_path, 'w') as configfile:
            config.write(configfile)

    def create_history(self,history_path, project_name):
        #create history.txt in history_path
        name = "history.txt"
        history_path = os.path.join(history_path, name)

        #get time and date
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        with open(history_path, 'w') as f:
            f.write("%s Project '%s' created\n" % (dt_string , project_name))
            f.close
    
    def createProject(self,**kwargs):

        #Check Inputs
        if kwargs.get('path',None) == None:
            #Ask for Path
            tkinter.Tk().withdraw()
            parent_dir = askdirectory(title='Choose a path for your Project')
        else:
            parent_dir = kwargs.get('path',None)
     
        if not parent_dir:
            print("You have to choose a path to store the Project.")
            return
        
        if kwargs.get('name',None) == None:
            project_name = tkinter.simpledialog.askstring(title = 'Add Project', prompt = 'Please name your Project: ')
        else:
            project_name = kwargs.get('name',None)

        if not project_name:
            print("You have to name your Project.")
            return

        path = os.path.join(parent_dir, project_name)

        #check for error
        try:  
            os.mkdir(path)  
        except OSError as error:  
            print(error)
        
        #create project conf
        self.create_config(path, project_name)

        #create history file
        self.create_history(path, project_name)
        print("The Project '%s' was created." % project_name)
        return

    def add_measurement_series(self,**kwargs):

        #Check Input
        if None in kwargs.values():
            #Ask for Path
            tkinter.Tk().withdraw()
            parent_dir = askdirectory(title = 'Choose the Project')
        else:
            parent_dir = kwargs.get('path',None)

        #check for config file
        config_name = "config.ini"
        config_path = os.path.join(parent_dir,config_name)
        if os.path.exists(config_path):
            config = configparser.ConfigParser()
            config.read(config_path)
            project_name = config.get('Database', 'p_name')
            print("'%s' is a valid Project." % project_name)
        else:
            print("Your Directory is not a valid BiVital-Directory")
            return
        
        #create directory
        if kwargs.get('name',None) == None:
            directory = tkinter.simpledialog.askstring(title = 'Add Measurement Series', prompt = 'Please name your Measurement Series: ')
        else:
            directory = kwargs.get('name', None)

        path = os.path.join(parent_dir, directory, "Label")
        mode = 0o666
        #check for error
        try: 
            os.makedirs(path,mode, exist_ok = False) 
            print("Directory '%s' created successfully" % directory) 
        except OSError as error: 
            print("Directory '%s' can not be created" % directory)
        
        #write to history file
        self.write_history(parent_dir, directory,'Series')

    def write_history(self,parent_dir, directory, type):
        #create history.txt in history_path
        name = "history.txt"
        history_path = os.path.join(parent_dir, name)

        #get time and date
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        if type == 'Data':
            with open(history_path, 'a') as f:
                f.write("%s Data from '%s' loaded\n" % (dt_string , directory))
                f.close
            return
        elif type == 'Series':
            with open(history_path, 'a') as f:
                f.write("%s Measurement Series: '%s' and empty Label-Directory created\n" % (dt_string , directory))
                f.close
            return
        elif type == 'Label':
            with open(history_path, 'a') as f:
                f.write("%s Label file from '%s' added to Label-Directory\n" % (dt_string, directory))
                f.close
            return
    
    def add_data(self, **kwargs):

        #Check Input
        if kwargs.get('path',None) == None:
            #Ask for Path
            tkinter.Tk().withdraw()
            measurement_path = askdirectory(title = 'Choose the measurement series')
        else:
            measurement_path = kwargs.get('path',None)
        
        project_path = os.path.dirname(measurement_path)
        #check if Project is valid
        config_name = "config.ini"
        config_path = os.path.join(project_path,config_name)
        if os.path.exists(config_path):
            config = configparser.ConfigParser()
            config.read(config_path)
            project_name = config.get('Database', 'p_name')
            data_flag = config.get('General', 'biVital_data')
            print("'%s' is a valid Project." % project_name)
        else:
            print("Your Directory is not a valid BiVital-Directory")
            return

        #Check kwargs
        if kwargs.get('source',None) == None:
            root = tkinter.Tk()
            root.title("Choose Data Source")
            root.geometry("300x200")
            label = tkinter.Label(root, text="Choose Data Source")
            label.pack()
            button1 = tkinter.Button(root, text="BiVital", command = lambda: self.load_data(measurement_path, project_path, True, data_flag))
            button1.pack()
            button2 = tkinter.Button(root, text="PC", command = lambda: self.load_data(measurement_path, project_path, False, data_flag))
            button2.pack()
            button3 = tkinter.Button(root, text="Quit", command = lambda: [root.quit(), root.destroy()])
            button3.pack()
            root.mainloop()
        else:
            if kwargs.get('source',None) == 'bivital':
                self.load_data(measurement_path, project_path, True, data_flag)
            else:
                self.load_data(measurement_path, project_path,False, data_flag)
        return
    
    def load_data(self, measurement_path, project_path, source, data_flag):
        if source:
            mac, file = self.builtup_serial_connection(measurement_path)

            if not mac or not file:
                print("❌ No data loaded from BI-Vital.")
                return

            origin = f"BiVital {mac}"
            self.write_history(project_path, origin, 'Data')
            if data_flag == 'False':
                config = configparser.ConfigParser()
                config.read(os.path.join(project_path, "config.ini"))
                config.set('General', 'biVital_data', 'True')
                with open(os.path.join(project_path, "config.ini"), 'w') as configfile:
                    config.write(configfile)
            print("✅ Data from BI-Vital added.")

        else:
            file_path = askopenfilename(title='Choose the data file')

            if not file_path:
                print("⚠️ No file selected.")
                return

            if not file_path.endswith('.csv'):
                print("❌ The file must be a .csv file.")
                return

            # Read BiVital ID from the file
            id_call = "BI-Vital"
            bivital_id = None

            try:
                with open(file_path, newline='') as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    for row in csv_reader:
                        if id_call in str(row):
                            parts = str(row[0]).split(" ")
                            if len(parts) > 1:
                                bivital_id = parts[1]
                            break
            except Exception as e:
                print(f"❌ Failed to read the CSV file: {e}")
                return

            if not bivital_id:
                print("❌ Could not find a BI-Vital ID in the CSV file.")
                return

            # Prepare destination directory
            dest_path = os.path.join(measurement_path, bivital_id)
            try:
                os.makedirs(dest_path, exist_ok=True)
                print(f"📁 Directory prepared: {dest_path}")
            except OSError as e:
                print(f"❌ Failed to create directory: {e}")
                return

            try:
                shutil.copy(file_path, dest_path)
                self.write_history(project_path, file_path, 'Data')
                if data_flag == 'False':
                    config = configparser.ConfigParser()
                    config.read(os.path.join(project_path, "config.ini"))
                    config.set('General', 'biVital_data', 'True')
                    with open(os.path.join(project_path, "config.ini"), 'w') as configfile:
                        config.write(configfile)
                print("✅ Data from PC added.")
            except Exception as e:
                print(f"❌ Failed to copy file: {e}")
    

    def builtup_serial_connection(self, path, *args, **kwargs):
        print("\n🔌 Trying to connect with BI-Vital...")

        try:
            with serial.serial_for_url('hwgrep://1F00:B151') as s:
                s.baudrate = 1000000
                s.timeout = 0.01
                s.setDTR(True)
                time.sleep(0.1)

                s.write(b'echo off\n')
                time.sleep(0.5)
                s.read_all()

                BiVitalMac = self.GetBiVitalMAC(s)
                print(f"✅ Detected BI-Vital: {BiVitalMac}")

                # Get available files first (before making folder)
                files = self.GetAvailableFileNames(s)

                if not files:
                    print("⚠️ No files found in flash storage.")
                    return None, None

                # Now create directory only if files exist
                target_path = os.path.join(path, BiVitalMac)
                os.makedirs(target_path, exist_ok=True)
                print(f"📁 Created directory: {target_path}")

                # User file selection
                if len(files) > 1:
                    print("📦 Multiple files found:")
                    for i, file in enumerate(files):
                        print(f"  [{i}] {file}")

                    file_index = tkinter.simpledialog.askinteger(
                        title='Choose a file',
                        prompt='Enter the index of the file to download or type -1 for all: '
                    )

                    if file_index == -1:
                        for fname in files:
                            fpath = os.path.join(target_path, fname)
                            with open(fpath, mode='wb') as f:
                                self.DownloadFile(s, f"/logs/{fname}", f)
                        return BiVitalMac, files

                    elif 0 <= file_index < len(files):
                        fname = files[file_index]
                        fpath = os.path.join(target_path, fname)
                        with open(fpath, mode='wb') as f:
                            self.DownloadFile(s, f"/logs/{fname}", f)
                        return BiVitalMac, fname

                    else:
                        print("❌ Invalid file index.")
                        return None, None

                else:
                    # Only one file, download it
                    fname = files[0]
                    fpath = os.path.join(target_path, fname)
                    with open(fpath, mode='wb') as f:
                        self.DownloadFile(s, f"/logs/{fname}", f)
                    return BiVitalMac, fname

        except serial.SerialException as e:
            print("❌ Serial connection failed:", str(e))
            return None, None
        except Exception as e:
            print("❌ Unexpected error:", str(e))
            return None, None

            
            
    def close_serial_connection(self, s):
        #Close Serial Connection
        try:
            s.open()
            s.write(b'echo on\n')
            time.sleep(0.2)
            s.read_all()
            s.setDTR(False)
            time.sleep(1)
            s.close()
        except:
            pass

    def download_serial(self,*args, **kwargs):
        print ("\nDownload files from flash storage... ", end='')
        try:
            with serial.serial_for_url('hwgrep://1F00:B151') as s:
                s.baudrate = 1000000
                s.timeout = 0.01
                s.setDTR(True)
                time.sleep(0.1)

                s.write(b'echo off\n')
                time.sleep(0.5)
                s.read_all()
                print("✅ Connected to BI-Vital:", self.GetBiVitalMAC(s), "\n")

                files = self.GetAvailableFileNames(s)
                if not files:
                    print("⚠️ No files found on the BI-Vital flash storage.")
                    return
                
                mydir = ''
                if 'path' in kwargs:
                    project_path = kwargs['path'] + '\\'
                    mydir = os.path.join(os.getcwd(), "logs\\" + project_path + about_mac + "\\")
                else:
                    mydir = os.path.join(os.getcwd(), "logs\\" + about_mac + "\\" + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + "\\")
                
                try:
                    os.makedirs(mydir)
                    print("📁 Created output directory: ", mydir)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise  # This was not a "directory exist" error..

                f = open(mydir + "LogConf.txt", mode='wb')#, encoding='utf-8')
                self.DownloadFile(s, "/LogConf.txt", f)
                print("\x1b[2A\r📝 Saved " + f.name + "\x1b[0K", end='\n\x1b[0K', flush=True)

                f = open(mydir + "about.txt", mode='w', encoding='utf-8')
                f.write(about)
                f.close()
                print("📝 Saved " + f.name)

                files = self.GetAvailableFileNames(s)
                count = 0
                if len(files) > 0:
                    for file in files:
                        count += 1
                        print("⬇️", str(count) + "/" + str(len(files)) + " Download file: " + file)
                        f = open(mydir + file, mode='wb')
                        self.DownloadFile(s, "/logs/" + file, f)
                        print("\x1b[2A\r✅ Saved " + f.name + "\x1b[0K", end='\n\x1b[0K', flush=True)

        except serial.SerialException as e:
            print("❌ Serial connection failed:")
            print(str(e))
        except Exception as e:
            print("❌ Unexpected error during download:")
            print(str(e))
        else:
            print("\n✅ All files downloaded successfully.")
        finally:
            #Close Serial Connection
            try:
                s.write(b'echo on\n')
                time.sleep(0.2)
                s.read_all()
                s.setDTR(False)
                time.sleep(1)
                s.close()
            except:
                pass

    def GetAvailableFileNames(self, s):
        """
        Get log file names from BiVital flash storage

        :param s: open serial connection
        :return: list of file names
        """
        try:
            s.read_all()
            time.sleep(1)
            s.write(b'ls /logs\r\n')
            time.sleep(1)

            response = s.read_all().decode('ascii', errors='ignore')

            if '..' not in response:
                print("⚠️ Unexpected response from device. No file listing found.")
                return []

            # Extract file list
            ls_ans = response[response.find('..'):].split("\n")
            files = []

            for line in ls_ans:
                if ".csv" in line or ".wav" in line:
                    line = line.replace('\r', '').replace(" ", "")
                    files.append(line)

            if files:
                print(f"\n📦 Found {len(files)} files in flash storage: {files}")
            else:
                print("\n📂 No .csv or .wav files found in flash storage.")

            return files

        except Exception as e:
            print(f"❌ Failed to list files: {e}")
            return []

    def DownloadFile(self, s, full_path, dst_file):
        print_file_cmd = 'cat ' + str(full_path) + "\n"
        s.write(print_file_cmd.encode())
        time.sleep(0.2)

        # First line is always the file name
        max_attempts = 10  # arbitrary limit to prevent infinite loops; adjust as needed
        attempt = 0

        while attempt < max_attempts:
            new_reading = str(s.readline().decode("utf-8", errors='ignore'))
            if "File /" in new_reading:
                file_name = new_reading.replace('File ', '').replace(' ', '').replace('\r', '').replace('\n', '')
                assert file_name == full_path
                break  # exit the loop once the condition is met
            attempt += 1

        # If you've looped max_attempts times and didn't find the string, raise the exception
        else:
            raise Exception("Error: File name not found")

        #Second line is alway hint 
        new_reading = str(s.readline().decode("utf-8", errors='ignore'))
        if not "Press (a) to abort process" in new_reading:
            raise Exception("Error: Missed abort hint [", new_reading, "]")


        new_reading = str(s.readline().decode("utf-8", errors='ignore'))
        if "Total size " in new_reading:
            file_size = new_reading[new_reading.find('Total size '):new_reading.find(' bytes:')]
            file_size = int(file_size.replace('Total size ', '').replace(' ', '').replace('\r','').replace('\n',''))
            print("File size: ", self.sizeof_fmt(file_size))
        else:
            raise Exception("Error: File size not found")

        # Second line is always the Start of File indicator
        new_reading = str(s.readline().decode("utf-8", errors='ignore'))
        if "--- Start of File ---" in new_reading:
            #print("Start to download ", full_path)

            #Get Payload RAW
            read_bytes = 0
            percent = float(1) #catch empty files
            last_update = time.time()
            while read_bytes < file_size :
                new_reading = s.read(min(2048, file_size - read_bytes))
                dst_file.write(bytearray(new_reading))
                read_bytes += len(new_reading)

                if(time.time() - last_update > 0.5):
                    last_update = time.time()

                    #calculate progress of download
                    if(file_size > 0):
                        percent = float(read_bytes)/float(file_size)
                    progress = "{:3.2f}".format(percent*100.0)
                    print("Progress:", progress, "%", end='\r', flush=True)

            dst_file.close()
            if(read_bytes == file_size):
                print("\rComplete", end='\r', flush=True)
            else:
                raise Exception("Error: File size mismatch")
        else:
            raise Exception("Error: Start of File not found")
        
        assert(s.read(1) == b'\n')
        
        # Last line is always the End of File indicator
        new_reading = str(s.readline().decode("utf-8", errors='ignore'))

        if "--- End of File ---" in new_reading:
            print("Download successfull", full_path)
            return 
        else:
            raise Exception("Error: End of File not found")

    def GetBiVitalMAC(self,s):
        global about, about_mac
        s.read_all()
        time.sleep(1)
        s.write(b'about\r\n')
        time.sleep(1)
        about = str(s.read_all().decode('ascii'))
        try:
            about_mac = about[about.index("Name: BI-Vital ") : about.index("\nMAC: ")]
            about_mac = about_mac.replace("Name: BI-Vital ", "")
            about_mac = about_mac.replace(" ", "")
            assert len(about_mac) == 4
        except:
            print(about)
            raise Exception("No BI-Vital found")

        return about_mac
    
    def sizeof_fmt(self,num, suffix="B"):
        for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
            if abs(num) < 1024.0:
                return f"{num:3.1f}{unit}{suffix}"
            num /= 1024.0
        return f"{num:.1f}Yi{suffix}"
    
    def add_label(self, **kwargs):
        #Check Input
        if kwargs.get('path',None) == None:
            #Ask for Path
            tkinter.Tk().withdraw()
            measurement_path = askdirectory(title = 'Choose the Series for the Label')
        else:
            measurement_path = kwargs.get('path',None)

        #check for config file
        config_name = "config.ini"
        project_path = os.path.dirname(measurement_path)
        config_path = os.path.join(project_path + '/' + config_name)
        print(config_path)
        if os.path.exists(config_path):
            config = configparser.ConfigParser()
            config.read(config_path)
            project_name = config.get('Database', 'p_name')
            print("'%s' is a valid Series." % project_name)
        else:
            print("Your Directory is not a valid BiVital-Series-Directory")
            return
        
        #Add Label file from PC to Label directory
        #choose a file
        file_path = askopenfilename(title = 'Choose the label file')
        #copy label file to directory
        label_directory = os.path.join(measurement_path, "Label")
        if os.path.basename(file_path) != 'label.csv':
            shutil.copy(file_path, os.path.join(label_directory, 'label.csv'))
            print("Label file renamed to 'label.csv'")
        else:
            shutil.copy(file_path, label_directory)
        print("Label file added")

        self.write_history(project_path, file_path, 'Label')
        return
    
    def open_example(self):
        """
        Lists all example Jupyter notebooks in the 'bivital.example' package,
        prompts the user to choose one, then opens a temporary copy in Jupyter Notebook.
        Changes will not affect the original bundled file.
        """
        # Locate the directory inside the package
        example_dir = files("bivital.example")

        # List all Jupyter notebooks
        notebooks = [p for p in example_dir.iterdir() if p.suffix == ".ipynb"]
        
        if not notebooks:
            print("No Example notebooks available")
            return

        # Print notebook options
        print("Available example notebooks:")
        for idx, nb in enumerate(notebooks):
            print(f"{idx}: {nb.name}")

        # Get user selection
        while True:
            try:
                choice = int(input("Enter the number of the notebook to open: "))
                if 0 <= choice < len(notebooks):
                    break
                else:
                    print("Invalid number. Please choose a valid index.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        selected_notebook = notebooks[choice]

        # Create a temporary directory and copy the selected notebook into it
        tmp_dir = tempfile.mkdtemp()
        tmp_path = shutil.copy(selected_notebook, tmp_dir)

        print(f"Opening temporary copy at: {tmp_path}")
        print("Any changes you make will not affect the original.")

        # Launch Jupyter to open the notebook
        subprocess.run(["jupyter", "notebook", tmp_path], check=True)





            