#!/usr/bin/python
import os
import shutil
import subprocess


def download():
    """
    Downloads all files from this bucket using the AWS CLI tool.
    """

    subprocess.call("aws s3 cp --recursive s3://mqlibinstances .", shell=True)


def cleanup():
    """
    Collects files into folders based on prefix (e.g. be50, culberson).
    Unzips the files after moving.
    """

    folders = ["be500", "be1000", "be2500", "be50", "be100", "be250",
               "culberson", "gka", "g", "G", "p", "imgseg"]

    for folder in folders:
        print("Starting to process {}".format(folder))
        if not os.path.exists(folder):
            os.makedirs(folder)

        files_to_move = [filename for filename in os.listdir('.') if
                         filename.startswith(folder) and
                         filename.endswith(".zip")]

        for myfile in files_to_move:
            shutil.move(myfile, folder)
            subprocess.call("unzip {}/{}".format(folder, myfile), shell=True,
                            stdout=open(os.devnull, "w"),
                            stderr=subprocess.STDOUT)
            subprocess.call("rm {}/{}".format(folder, myfile), shell=True,
                            stdout=open(os.devnull, "w"),
                            stderr=subprocess.STDOUT)

        print("{} files processed for {}".format(len(files_to_move), folder))
    print("Cleanup complete!")


if __name__ == "__main__":
    download()
    cleanup()
