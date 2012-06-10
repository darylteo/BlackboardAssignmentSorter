import os
import shutil
import re
import argparse
from collections import namedtuple

File = namedtuple('File','groupname attempt shortname fullfile')

def main():
    fromdir = args.source
    todir = args.destination
    logfile = os.path.join(args.destination,'sort.log')

    # grab the file list
    files = os.listdir(fromdir)

    # sort the files 
    groups = sort_groups(files)

    # distribute
    distribute(groups, todir)

    # generate a submission
    results = generate_log(groups)
    write_log(logfile,results)
    

# take a list of file strings representing filenames
# files must be top level (not in a directory)
def sort_groups(files):
    # compile regex for parsing the string
    regex = re.compile('(?P<fullfile>.*?_(?P<groupname>.+?)_attempt_(?P<attempt>.+?)(_(?P<name>.+?))?\.(?P<ext>.*))')

    # stores groups
    groups = dict()
    
    for file in files:
        matches = regex.match(file)

        if(matches):
            print_log('File Found: ' + file)
        
            groupname,attempt,name,ext,fullfile = matches.group('groupname','attempt','name','ext','fullfile')
            # grr, sometimes group names have trailing spaces... stupid blackboard
            # try to avoid causing this
            groupname = groupname.strip()

            if(name is None):
                name = 'comments'

            # create a list of files for this group
            if(groupname not in groups):
                groups[groupname] = list()

            shortname = name + '.' + ext;
            groups[groupname].append(File(groupname,attempt,shortname,fullfile))

    return groups

# given all the groups, will create folders for each group,
# and in each group, a folder for each attempt.
# files will then be moved to their respective attempt folder
def distribute(groups, destination):

    # create the target folder
    # will overwrite the entire folder if it already exists
    def setup_target_folder(folder):
        if (os.path.isdir(folder)):
            shutil.rmtree(folder)

        os.makedirs(folder)

    # creates a attempt folder in the group folder if
    # the attempt folder does not exist
    def setup_attempt_folder(folder):
        if (os.path.isdir(folder)):
            return

        os.makedirs(folder)

    # copies the target file to the destination
    def copy_file(fromfile,destinationfile):
        if not os.path.isfile(fromfile):
            return

        shutil.copyfile(fromfile,destinationfile)

    # prepare the target folder
    setup_target_folder(destination)
    
    for group in groups:
        files = groups[group]

        for file in files:
            # setup the folder if necessary
            target = os.path.join(destination,file.groupname,file.attempt)
            setup_attempt_folder(target)

            # move the file
            target = os.path.join(target, file.shortname)
            
            print_log('Copying File:\nSource: ' + file.fullfile + '\nTarget: ' + target + '\n')
            copy_file(file.fullfile,target)

def generate_log(groups):
    dateregex = re.compile('(?P<year>\d+?)-(?P<month>\d+?)-(?P<day>\d+?)-(?P<hour>\d+?)-(?P<min>\d+?)-(?P<sec>\d+)')

    def string_to_date(string):
        matches = dateregex.match(string)

        year,month,day,hour,minutes,sec = matches.group('year','month','day','hour','min','sec')
        return '-'.join((year,month,day)) + ' ' + ':'.join((hour,minutes,sec))
        
    attempts = dict()

    for group in groups:
        files = groups[group]

        attempt = '';
        
        for file in files:
            if (file.attempt > attempt):
                attempt = file.attempt

        attempts[group] = string_to_date(attempt)

    return attempts

def write_log(file,attempts):
    f = open(file,'w')

    if(f == None):
        print("Could not open log file", file=sys.stderr)

    for group in attempts:
        attempt = attempts[group]

        print(group,attempt, sep=",",file=f)

    f.flush()
    f.close()

def parse_args():
    working = os.getcwd()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v',
        '--verbose',
        dest='verbose',
        help='Displays verbose sorting information',
        
        action='store_const',
        const=True,
        default=False
    )
      
    parser.add_argument(
        '-s',
        '--source',
        dest='source',
        help='Directory where original files are stored.',
        
        default=None,
        metavar='source'
    )
  
    parser.add_argument(
        '-d',
        '--destination',
        dest='destination',
        default=None, # working directory
        help='Directory where files will be sorted into.',
        metavar='destination'
    )
    
    args = parser.parse_args()
    
    if not (args.source):
        args.source = working
        
    if not (args.destination):
        args.destination = os.path.join(working,'sorted')
    
    return args
    
def print_log(msg):
    if(args.verbose):
        print(msg)
    
# begin
args = parse_args()
print_log(args)

main()
