import os
import shutil
import re
from collections import namedtuple

File = namedtuple('File','groupname attempt shortname fullfile')


def main():
    working = os.getcwd()

    fromdir = working
    todir = os.path.join(working,'sorted')

    # grab the file list
    files = os.listdir(fromdir)

    # sort the files 
    groups = sort_groups(files)

    # distribute
    distribute(groups, todir)

    # generate a submission
    results = generate_log(groups)

    for group in results:
        attempt = results[group]
        print(group + ',' + attempt)
    

# take a list of file strings representing filenames
# files must be top level (not in a directory)
def sort_groups(files):
    # compile regex for parsing the string
    regex = re.compile('(?P<fullfile>.*?_(?P<groupname>.+?)_attempt_(?P<attempt>.+?)(_(?P<name>.+?))?\.(?P<ext>.*))')

    # stores groups
    groups = dict()
    
    for file in files:
        matches = regex.match(file)

        print(file)
        if(matches):
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
            copy_file(file.fullfile,target)

def generate_log(groups):
    dateregex = re.compile('(?P<year>\d+?)-(?P<month>\d+?)-(?P<day>\d+?)-(?P<hour>\d+?)-(?P<min>\d+?)-(?P<sec>\d+)')

    def string_to_date(string):
        print(string)
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
# begin
main()
