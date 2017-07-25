#!/usr/bin/env python

import zipfile
import xlsxwriter
import xlrd
import vcf
import time
import sys
import subprocess
import smtplib,ssl
import shutil
import regex
import re
import pandas as pd
import os
import multiprocessing
import gzip
import glob
import git
import csv
from optparse import OptionParser
from optparse import OptionParser
from numpy import mean
from functools import partial
from email.utils import formatdate
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from distutils.dir_util import copy_tree
from datetime import datetime
from datetime import datetime
from concurrent import futures
from concurrent import futures
from collections import OrderedDict
from collections import OrderedDict
from collections import Counter
from Bio.SeqIO.QualityIO import FastqGeneralIterator
from Bio import SeqIO
try:
    from ete3 import Tree, TreeStyle, NodeStyle, TextFace, faces, AttrFace
    ete3_available = True
except:
    ete3_available = False
    pass
try:
    from xvfbwrapper import Xvfb
    xvfb_available = True
except:
    xvfb_available = False
    pass

###############################################
###############################################
##################script1######################
###############################################
###############################################

class script1():

        '''A script1 object.  These objects have the following properties:
        Attributes:
            fastq_R1
            fastq_R2 '''

        def __init__( self, fastq_R1, fastq_R2, species=None):
            '''instantiate object whose name *name*.  Proved species to force refernce type'''
    #        self.fastq_R1=fastq_R1
    #        self.fastq_R2=fastq_R2

            global R1
            global R2
            R1 = fastq_R1
            R2 = fastq_R2
            
            global gbk_file
            gbk_file = ""
            global in_annotation_as_dict
            #in_annotation_as_dict = {}
            
            global directory
            global zips
            directory = str(os.getcwd())
            zips = directory + "/zips"
            
            os.makedirs(zips)
            shutil.move(R1, zips)
            shutil.move(R2, zips)
            
            R1 = zips + "/" + R1
            R2 = zips + "/" + R2
            
            global R1unzip
            global R2unzip
            R1unzip = re.sub('\.gz', '', R1)
            R2unzip = re.sub('\.gz', '', R2)

            self.species = species
            
            if self.species:
                species_force = species
                print("Sample will be ran as %s" % self.species)
            else:
                species_force=None

            global dependents_dir
            global reference
            global hqs
            global email_list
            global upload_to
            global remote
            global script_dependents
            global spoligo_db
            
            global mlst_type
            global octalcode
            global sbcode
            global binarycode
            global ave_coverage
            global zero_coverage_vcf
            global genome_coverage

            ### SET PARAMETERS
            if species_force:
                option_list, found = script1.parameters(species_force)
                dependents_dir = option_list[0]
                reference = option_list[1]
                hqs = option_list[2]
                gbk_file = option_list[3]
                email_list = option_list[4]
                upload_to = option_list[5]
                remote = option_list[6]
                script_dependents = option_list[7]
                spoligo_db = option_list[8]

            else:
                best_ref_found = script1.best_reference(self)
                self.species = best_ref_found
                try: # exit if best ref isn't in parameter list
                    option_list, found = script1.parameters(best_ref_found)
                    dependents_dir = option_list[0]
                    reference = option_list[1]
                    hqs = option_list[2]
                    gbk_file = option_list[3]
                    email_list = option_list[4]
                    upload_to = option_list[5]
                    remote = option_list[6]
                    script_dependents = option_list[7]
                    spoligo_db = option_list[8]
                except UnboundLocalError:
                    print("\nprinted options list:")
                    for i in option_list:
                        print(i)
                    print("\nNo parameters options for best_ref_found or species given - UnboundLocalError\n\n")
                    self.species = "NO FINDINGS"
                except TypeError:
                    print("No parameters options for best_ref_found or species given - TypeError")
                    self.species = "NO FINDINGS"
            try:
                shutil.copy2(reference, directory)
                shutil.copy2(hqs, directory)
            except FileNotFoundError:
                time.sleep(5)
                shutil.copy2(reference, directory)
                shutil.copy2(hqs, directory)
            except NameError:
                print("No parameters options for best_ref_found or species given - NameError")
                self.species = "NO FINDINGS"

        def show_fastqs(self):
            '''show FASTQs being used'''
            print("R1: %s\nR2: %s" % (R1, R2))

        def sizeof_fmt(num, suffix='B'):
            for unit in ['','K','M','G','T','P','E','Z']:
                if abs(num) < 1024.0:
                    return "%3.1f%s%s" % (num, unit, suffix)
                num /= 1024.0
            return "%.1f%s%s" % (num, 'Yi', suffix)

        def unzipfiles(): # don't "self" if called from within
            for zip_filename in R1, R2:
                print("Unzipping... %s" % zip_filename)
                name_nogz = os.path.splitext(zip_filename)[0]
                write_out = open(name_nogz, 'wt')
                with gzip.open(zip_filename, 'rt') as f:
                    file_content = f.read()
                    print(file_content, file=write_out)
                write_out.close()

        def update_directory(dependents_dir): # UPDATE DIRECTORIES
            home = os.path.expanduser("~")
            
            if os.path.isdir("/bioinfo11/TStuber/Results"): #check bioinfo from server
                upload_to = "/bioinfo11/TStuber/Results"
                remote="/bioinfo11/TStuber/Results" + dependents_dir
                if os.path.isdir("/Users/Shared"):
                    dep_path = "/Users/Shared"
                    dir_split = dependents_dir.split('/')[1:]
                    for i in dir_split:
                        dep_path += '/' + i
                        if not os.path.exists(dep_path):
                            os.makedirs(dep_path)
                    local = "/Users/Shared" + dependents_dir
                    if os.path.isdir(local):
                        try:
                            shutil.rmtree(local)
                            shutil.copytree(remote, local)
                        except:
                            pass
                elif os.path.isdir("/home/shared"):
                    dep_path = "/home/shared"
                    dir_split = dependents_dir.split('/')[1:]
                    for i in dir_split:
                        dep_path += '/' + i
                        if not os.path.exists(dep_path):
                            try:
                                os.makedirs(dep_path)
                            except:
                                pass
                    local = "/home/shared" + dependents_dir
                    if os.path.isdir(local):
                        try:
                            shutil.rmtree(local)
                            shutil.copytree(remote, local)
                        except:
                            pass

            elif os.path.isdir("/Volumes/root/TStuber/Results"): #check bioinfo from Mac
                upload_to = "/Volumes/root/TStuber/Results"
                remote="/Volumes/root/TStuber/Results" + dependents_dir
                if os.path.isdir("/Users/Shared"):
                    dep_path = "/Users/Shared"
                    dir_split = dependents_dir.split('/')[1:]
                    for i in dir_split:
                        dep_path += '/' + i
                        if not os.path.exists(dep_path):
                            os.makedirs(dep_path)
                    local = "/Users/Shared" + dependents_dir
                    if os.path.isdir(local):
                        try:
                            shutil.rmtree(local)
                            shutil.copytree(remote, local)
                        except:
                            pass
                elif os.path.isdir("/home/shared"):
                    dep_path = "/home/shared"
                    dir_split = dependents_dir.split('/')[1:]
                    for i in dir_split:
                        dep_path += '/' + i
                        if not os.path.exists(dep_path):
                            try:
                                os.makedirs(dep_path)
                            except:
                                pass
                    local = "/home/shared" + dependents_dir
                    if os.path.isdir(local):
                        try:
                            shutil.rmtree(local)
                            shutil.copytree(remote, local)
                        except:
                            pass

            #### PLACE A CHECK FROM GITHUB
            
            elif os.path.isdir("/Users/Shared" + dependents_dir): #check local copy in shared folder
                upload_to ="not_found"
                remote = "not_found"
                local = "/Users/Shared" + dependents_dir
                    
            elif os.path.isdir("/home/shared" + dependents_dir): #check local copy in shared folder
                upload_to ="not_found"
                remote = "not_found"
                local = "/home/shared" + dependents_dir
            
            elif os.path.isdir(home + "/dependencies" + dependents_dir): #check local copy from Git repo
                upload_to ="not_found"
                remote = "no remote"
                script_location = home # points to home directory
                local = home + "/dependencies" + dependents_dir # sets dependencies directory to home directory
            else:
                try:
                    os.makedirs(home + "/dependencies")
                    print("\n\nDOWNLOADING DEPENDENCIES FROM GITHUB... ***\n\n")
                    git.Repo.clone_from("https://github.com/stuber/dependencies.git", home + "/dependencies")
                    upload_to ="not_found"
                    remote = "no remote"
                    script_location = home # points to home directory
                    local = home + "/dependencies" + dependents_dir # sets dependencies directory to home directory
                except FileExistsError:
                    upload_to ="not_found"
                    remote = "no remote"
                    script_location = home # points to home directory
                    local = home + "/dependencies" + dependents_dir # sets dependencies directory to home directory
                    pass
                
            print("\n####################DIRECTORY LOCATION")
            print("####################upload_to: %s" % upload_to)
            print("####################remote: %s" % remote)
            print("####################local: %s\n" % local)
            
            return upload_to, remote, local

        def get_annotations(line, in_annotation_as_dict): #for line in vfile
            #pos_found = False
            line=line.rstrip()
            if line.startswith("#"): # save headers to file
                return(line)
            elif not line.startswith("#"): # position rows
                #pos_found = False
                split_line = line.split('\t')
                chrom = split_line[0]
                position = split_line[1] # get position
            #print ("Getting annotations")
                for each_key, each_value in in_annotation_as_dict.items():
                    pos_found = False
                    if chrom == each_key:
                        for feature in each_value.features:
                            position = int(position)
                            #print(position)
                            if position in feature and "CDS" in feature.type:
                                myproduct = "none list"
                                mylocus = "none list"
                                mygene = "none list"
                                for p in feature.qualifiers['product']:
                                    myproduct = p
                                for l in feature.qualifiers['locus_tag']:
                                    mylocus = l
                                if "gene" in feature.qualifiers:
                                    gene = feature.qualifiers['gene']
                                    for g in gene:
                                        mygene = g
                                annotation_found = myproduct + ", gene: " + mygene + ", locus_tag: " + mylocus
                                pos_found = True
                    if pos_found == False:
                        annotation_found = "No annotated product"
                    #print(annotation_found)
                    split_line[2] = annotation_found
                    annotated_line = "\t".join(split_line)
                    return(annotated_line)

        def parameters(give_option):
            if give_option == "ab1":
                found=True
                #Remove network path at and left of "Results"
                dependents_dir="/brucella/abortus1/script_dependents/script1"
                upload_to, remote, script_dependents = script1.update_directory(dependents_dir) #***FUNCTION CALL
                
                spoligo_db = script_dependents + "/nospoligo.txt"
                reference = script_dependents + "/NC_00693c.fasta"
                print("Reference being used: %s" % reference)
                hqs = script_dependents + "/NC_00693cHighestQualitySNPs.vcf"
                gbk_file = script_dependents + "/NC_006932-NC_006933.gbk"
                email_list = "tod.p.stuber@aphis.usda.gov"
                
                option_list=[dependents_dir, reference, hqs, gbk_file, email_list, upload_to, remote, script_dependents, spoligo_db]
                return option_list, found
            
            if give_option == "ab3":
                found=True
                #Remove network path at and left of "Results"
                dependents_dir="/brucella/abortus3/script_dependents/script1"
                upload_to, remote, script_dependents = script1.update_directory(dependents_dir) #***FUNCTION CALL
                
                spoligo_db = script_dependents + "/nospoligo.txt"
                reference = script_dependents + "/CP007682-7683c.fasta"
                print("Reference being used: %s" % reference)
                hqs = script_dependents + "/CP007682-7683cHighestQualitySNPs.vcf"
                gbk_file = script_dependents + "/CP007682-CP007683.gbk"
                email_list = "tod.p.stuber@aphis.usda.gov"
                

                option_list=[dependents_dir, reference, hqs, gbk_file, email_list, upload_to, remote, script_dependents, spoligo_db]
                return option_list, found
            
            if give_option == "canis":
                found=True
                #Remove network path at and left of "Results"
                dependents_dir="/brucella/canis/script_dependents/script1"
                upload_to, remote, script_dependents = script1.update_directory(dependents_dir) #***FUNCTION CALL
                
                spoligo_db = script_dependents + "/nospoligo.txt"
                reference = script_dependents + "/BcanisATCC23365.fasta"
                print("Reference being used: %s" % reference)
                hqs = script_dependents + "/canisHighestQualitySNPs.vcf"
                gbk_file = script_dependents + "/NC_010103-NC_010104.gbk"
                email_list = "tod.p.stuber@aphis.usda.gov"
                
                option_list=[dependents_dir, reference, hqs, gbk_file, email_list, upload_to, remote, script_dependents, spoligo_db]
                return option_list, found

            if give_option == "ceti1":
                found=True
                #Remove network path at and left of "Results"
                dependents_dir="/brucella/ceti1/script_dependents/script1"
                upload_to, remote, script_dependents = script1.update_directory(dependents_dir) #***FUNCTION CALL
                
                spoligo_db = script_dependents + "/nospoligo.txt"
                reference = script_dependents + "/Bceti1Cudo.fasta"
                print("Reference being used: %s" % reference)
                hqs = script_dependents + "/ceti1HighestQualitySNPs.vcf"
                gbk_file = None #script_dependents + "/no.gff"
                email_list = "tod.p.stuber@aphis.usda.gov"
                
                option_list=[dependents_dir, reference, hqs, gbk_file, email_list, upload_to, remote, script_dependents, spoligo_db]
                return option_list, found

            if give_option == "ceti2":
                found=True
                #Remove network path at and left of "Results"
                dependents_dir="/brucella/ceti2/script_dependents/script1"
                upload_to, remote, script_dependents = script1.update_directory(dependents_dir) #***FUNCTION CALL
                
                spoligo_db = script_dependents + "/nospoligo.txt"
                reference = script_dependents + "/Bceti2-TE10759.fasta"
                print("Reference being used: %s" % reference)
                hqs = script_dependents + "/ceti2HighestQualitySNPs.vcf"
                gbk_file = script_dependents + "/NC_022905-NC_022906.gbk"
                email_list = "tod.p.stuber@aphis.usda.gov"
                
                option_list=[dependents_dir, reference, hqs, gbk_file, email_list, upload_to, remote, script_dependents, spoligo_db]
                return option_list, found

            if give_option == "mel1":
                found=True
                #Remove network path at and left of "Results"
                dependents_dir="/brucella/melitensis-bv1/script_dependents/script1"
                upload_to, remote, script_dependents = script1.update_directory(dependents_dir) #***FUNCTION CALL
                
                spoligo_db = script_dependents + "/nospoligo.txt"
                reference = script_dependents + "/mel-bv1-NC003317.fasta"
                print("Reference being used: %s" % reference)
                hqs = script_dependents + "/mel-bv1-NC003317-highqualitysnps.vcf"
                gbk_file = script_dependents + "/NC_003317-NC_003318.gbk"
                email_list = "tod.p.stuber@aphis.usda.gov"
                
                option_list=[dependents_dir, reference, hqs, gbk_file, email_list, upload_to, remote, script_dependents, spoligo_db]
                return option_list, found

            if give_option == "mel2":
                found=True
                #Remove network path at and left of "Results"
                dependents_dir="/brucella/melitensis-bv2/script_dependents/script1"
                upload_to, remote, script_dependents = script1.update_directory(dependents_dir) #***FUNCTION CALL
                
                spoligo_db = script_dependents + "/nospoligo.txt"
                reference = script_dependents + "/mel-bv2-NC012441.fasta"
                print("Reference being used: %s" % reference)
                hqs = script_dependents + "/mel-bv2-NC012441-highqualitysnps.vcf"
                gbk_file = script_dependents + "/NC_012441-NC_012442.gbk"
                email_list = "tod.p.stuber@aphis.usda.gov"
                
                option_list=[dependents_dir, reference, hqs, gbk_file, email_list, upload_to, remote, script_dependents, spoligo_db]
                return option_list, found
                
            if give_option == "mel3":
                found=True
                #Remove network path at and left of "Results"
                dependents_dir="/brucella/melitensis-bv3/script_dependents/script1"
                upload_to, remote, script_dependents = script1.update_directory(dependents_dir) #***FUNCTION CALL
                
                spoligo_db = script_dependents + "/nospoligo.txt"
                reference = script_dependents + "/mel-bv3-NZCP007760.fasta"
                print("Reference being used: %s" % reference)
                hqs = script_dependents + "/mel-bv3-NZCP007760-highqualitysnps.vcf"
                gbk_file = script_dependents + "/NZ_CP007760-NZ_CP007761.gbk"
                email_list = "tod.p.stuber@aphis.usda.gov"
                
                option_list=[dependents_dir, reference, hqs, gbk_file, email_list, upload_to, remote, script_dependents, spoligo_db]
                return option_list, found

            if give_option == "suis1":
                found=True
                #Remove network path at and left of "Results"
                dependents_dir="/brucella/suis1/script_dependents/script1"
                upload_to, remote, script_dependents = script1.update_directory(dependents_dir) #***FUNCTION CALL
                
                spoligo_db = script_dependents + "/nospoligo.txt"
                reference = script_dependents + "/NC_017251-NC_017250.fasta"
                print("Reference being used: %s" % reference)
                hqs = script_dependents + "/B00-0468-highqualitysnps.vcf"
                gbk_file = script_dependents + "/NC_017251-NC_017250.gbk"
                email_list = "tod.p.stuber@aphis.usda.gov"
                
                option_list=[dependents_dir, reference, hqs, gbk_file, email_list, upload_to, remote, script_dependents, spoligo_db]
                return option_list, found

            if give_option == "suis4":
                found=True
                #Remove network path at and left of "Results"
                dependents_dir="/brucella/suis4/script_dependents/script1"
                upload_to, remote, script_dependents = script1.update_directory(dependents_dir) #***FUNCTION CALL
                
                spoligo_db = script_dependents + "/nospoligo.txt"
                reference = script_dependents + "/B-REF-BS4-40.fasta"
                print("Reference being used: %s" % reference)
                hqs = script_dependents + "/suis4HighestQualitySNPs.vcf"
                gbk_file = None #script_dependents + "/no.gff"

                email_list = "tod.p.stuber@aphis.usda.gov"
                
            if give_option == "ovis":
                found=True
                #Remove network path at and left of "Results"
                dependents_dir="/brucella/ovis/script_dependents/script1"
                upload_to, remote, script_dependents = script1.update_directory(dependents_dir) #***FUNCTION CALL
                
                spoligo_db = script_dependents + "/nospoligo.txt"
                reference = script_dependents + "/BovisATCC25840.fasta"
                print("Reference being used: %s" % reference)
                hqs = script_dependents + "/BovisATCC25840HighestQualitySNPs.vcf"
                gbk_file = None #script_dependents + "/no.gff"
                email_list = "tod.p.stuber@aphis.usda.gov"

                option_list=[dependents_dir, reference, hqs, gbk_file, email_list, upload_to, remote, script_dependents, spoligo_db]
                return option_list, found

            if give_option == "bovis":
                found=True
                #Remove network path at and left of "Results"
                dependents_dir="/mycobacterium/tbc/tbbov/script_dependents/script1"
                upload_to, remote, script_dependents = script1.update_directory(dependents_dir) #***FUNCTION CALL
                
                spoligo_db = script_dependents + "/spoligotype_db.txt"
                reference = script_dependents + "/NC_002945.fasta"
                print("Reference being used: %s" % reference)
                hqs = script_dependents + "/HighestQualitySNPs.vcf"
                gbk_file = script_dependents + "/NC_002945.gbk"
                email_list = "tod.p.stuber@aphis.usda.gov"
                
                option_list=[dependents_dir, reference, hqs, gbk_file, email_list, upload_to, remote, script_dependents, spoligo_db]
                return option_list, found
                
            if give_option == "af":
                found=True
                #Remove network path at and left of "Results"
                dependents_dir="/mycobacterium/tbc/af2122/script_dependents/script1"
                upload_to, remote, script_dependents = script1.update_directory(dependents_dir) #***FUNCTION CALL
                
                spoligo_db = script_dependents + "/spoligotype_db.txt"
                reference = script_dependents + "/NC_002945v4.fasta"
                print("Reference being used: %s" % reference)
                hqs = script_dependents + "/highqualitysnps.vcf"
                gbk_file = script_dependents + "/NC_002945v4.gbk"
                email_list = "tod.p.stuber@aphis.usda.gov"
                
                option_list=[dependents_dir, reference, hqs, gbk_file, email_list, upload_to, remote, script_dependents, spoligo_db]
                return option_list, found

            if give_option == "h37":
                found=True
                #Remove network path at and left of "Results"
                dependents_dir="/mycobacterium/tbc/h37/script_dependents/script1"
                upload_to, remote, script_dependents = script1.update_directory(dependents_dir) #***FUNCTION CALL
                
                spoligo_db = script_dependents + "/spoligotype_db.txt"
                reference = script_dependents + "/NC000962.fasta"
                print("Reference being used: %s" % reference)
                hqs = script_dependents + "/15-3162-highqualitysnps.vcf"
                gbk_file = script_dependents + "/NC_000962.gbk"
                email_list = "tod.p.stuber@aphis.usda.gov"
                
                option_list=[dependents_dir, reference, hqs, gbk_file, email_list, upload_to, remote, script_dependents, spoligo_db]
                return option_list, found

            if give_option == "para":
                found=True
                #Remove network path at and left of "Results"
                dependents_dir="/mycobacterium/avium_complex/para_cattle-bison/script_dependents/script1"
                upload_to, remote, script_dependents = script1.update_directory(dependents_dir) #***FUNCTION CALL
                
                spoligo_db = script_dependents + "/nospoligo.txt"
                reference = script_dependents + "/NC_002944.fasta"
                print("Reference being used: %s" % reference)
                hqs = script_dependents + "/HQ-NC002944.vcf"
                gbk_file = script_dependents + "/NC_002944.gbk"
                email_list = "tod.p.stuber@aphis.usda.gov"
                
                option_list=[dependents_dir, reference, hqs, gbk_file, email_list, upload_to, remote, script_dependents, spoligo_db]
                return option_list, found

        def finding_best_ref(v):
            count=0
            for fastq in R1unzip, R2unzip:
                with open(fastq) as in_handle:
                    # all 3, title and seq and qual, were needed
                    for title, seq, qual in FastqGeneralIterator(in_handle):
                        count += seq.count(v)
            return(v, count)
        
        def mlst(self):
        
            fastqs = glob.glob(zips + '/*.fastq')
            if len(fastqs) < 2:
                script1.unzipfiles()
            fastqs = glob.glob(zips + '/*.fastq')
            
            #https://bmcmicrobiol.biomedcentral.com/articles/10.1186/1471-2180-7-34
            write_ref = open("ST1-MLST.fasta", 'w')
            print(">ST1-MLST", file=write_ref)
            print("CGTTTCCCCAAGGAAGTGGAGGTTGCAGGCGATACGATCGATGTTGGCTACGGCCCGATCAAGGTTCATGCCGTCCGCAACCCGGCCGAACTGCCGTGGAAGGAAGAAAACGTCGATATCGCCCTTGAATGCACCGGCATTTTCACCTCGCGCGACAAGGCAGCACTTCATCTTGAAGCTGGCGCCAAGCGCGTCATCGTCTCCGCTCCCGCAGACGGTGCCGATCTCACCGTCGTCTATGGTGTCAACAACGACAAGCTGACGAAGGACCATCTGGTCATCTCCAACGCTTCGTGTACCACCAACTGCCTTGCGCCGGTGGCTCAGGTTCTCAACGATACTATCGGTATCGAAAAGGGCTTCATGACCACGATCCACTCCTATACGGGCGACCAGCCGACGCTGGACACCATGCACAAGGATCTCTACCGCGCCCGCGCCGCTGCCCTTTCCATGATCCCGACCTCGACGGGTGCGGCCAAGGCCGTCGGTCTCGTTCTGCCGGAACTGAAAGGCAAGCTCGACGGCGTTGCCATTCGCGTCCCGACCCCAAATGTCTCGGTCGTTGATCTCACCTTCATCGCCAAGCGTGAAACCACCGTTGAAGAAGTCAACAATGCGATCCGCGAAGCCGCCAATGGCCGCCTCAAGGGCATTCTCGGCTATACCGATGAGAAGCTCGTCTCGCACGACTTCAACCACGATTCCCATTCCTCGGTCTTCCACACCGACCAGACCAAGGTTATGGACGGCACCATGGTGCGTATCCTGTCGTGGTACGACAATGAATGGGGCTTCTCCAGCCGCATGAGCGACACCGCCGTCGCTTTGGGCAAGCTGATCTGATAACGGCAACGCCTCTCCTTCACTGGCGAGGCGTTTTCATTTCTTGATAAGGACCGAGAGAAGAAACATGATGTTCCGCACCCTTGACGATGCCAATGTCCAATCCAAGCGCGTGCTGGTCCGTGTTGACCTCAACGTGCCGAAAATCCGCCGTTCTGCTCGCTGGTCTTAACACCCCGGGCGTCACCACCGTGATCGAGCCGGTCATGACGCGCGATCATACGGAAAAGATGCTGCAAGACTTTGGCGCAGACCTGACGGTTGAAACCGATAAGGATGGTGTGCGCCATATCCGTATTGTCGGCCAGGGCAAGCTTACCGGCCAGACCATCGACGTGCCGGGTGATCCCTCGTCAACGGCTTTTCCGCTGGTGGCCGCCCTTCTGGTCGAAGGTTCGGAGGTCACCATCCGCAATGTGCTGATGAACCCGACCCGCACCGGCCTGATCCTGACGTTGCAGGAAATGGGGGCGGATATCGAGATCATCGATCCACGCCTTGCCGGCGGCGAGGATGTCGCCGATCTGCGCGTCAAGGCCTCGAAGCTGAAAGGCGTTGTCGTTCCGCCGGAACGTGCGCCTTCGATGATCGATGAATATCCGGTTCTGGCCATTGCCGCGTCTTTTGCGGAAGGCGAAACCGTGATGGACGGTCTCGATGAACTGCGCGTCAAGGAATCGGATCGTCTGGCGGCCGTTGCGCGCGGCCTTGAAGCCAATGGTGTCGATTGTACCGAAGGCGAGATGTCGCTGACGGTTCGTGGCCGCCCCGGCGGCAAGGGGCTGGGCGGTGGCACGGTTGCAACCCACCTCGACCACCGCATCGCGATGAGTTTCCTCGTCATGGGCCTTGCATCGGAAAAGCCGGTTACGGTGGATGACAGCACCATGATCGCCACCTCTTTCCCGGAATTCATGGGCATGATGGCGGGGCTGGGGGCGAAGATTGCCGAAAGCGGTGCAGAATGAAATCGTTCGTCGTCGCCCCGTTCATTGTCGCCATTGACGGACCGGCCGCCTCGGGCAAGGGAACCCTTGCCCGGCGGATCGCGACACATTACGGGATGCCGCATCTCGATACGGGCCTGACCTATCGCGCGGTCGCCAAGAGCCGCGCTCTGTCATTCTGGCCGTGGCAGGCCCGGTGGACGGCGACGAGATCGACCTCACCAATTGCGACTGGGTCGTGCGTCCTAAAAAGATGATCGCTGATCTGGGCTTTGAAGACGTGACCGTCCTCAATGATTTCGAGGCGCAGGCCCTTGCCGTGGTTTCGCTGGAAGGCCACCATATGGAACAGATCGGCGGCAAACCGGAGGAGGCTGTTGCCACCCGCGTCGTGCTCGGCCCCGGCACGGGCCTTGGCGTGGCAGGTCTGTTTCGCACACGTCATGCATGGGTTCCGGTTCCCGGTGAAGGCGGTCATATCGATATCGGTCCACGCACCGAACGCGACTACCAGATTTTCCCGCATATCGAACGCATCGAAGGGCGTGTCACCGGCGAGCAAATTCTTAGCGGGCGGGGCCTGCGCAACCTCTATCTGGGCATCTGCGCCGCCGACAAGATCACGCCCACCCTTGAGACGCCAGTAGACATTACATCCGCCGGACTGGACGGCAGCAATCCACAAGCCGCAGAAACGCTTGACCTCTTCGCCACCTATCTGGGGCGGCTTGCGGGCGACCTTGCGCTCATTTTCATGGCGCATGGCGGCGTTTATCTTTCGGGTGGCATCCCGGTGCGCATCCTTTCCGCCCTCAAGGCCGGTTCGTTCCGCGCAACCTTCGAGGACAAGGCCCCGCACAAGGCCATCATGCGCGACATACCGGTCCGCGTTATCACATATCAACTGGCGGCCTTAACCGGGCTTTCCGCTTTCGCCCGCACCCCCTCGCGCTTTGAAGTTTCGACCGAGGGCCGCCGCTGGCGCATGCGCCGCTAGAGCATTTCCGAGCCAAAAGTGCGAAGCGGTTCCGTTTCCCAACGAGCCGACCGCGGCTGCGCTTGCCTATGGTCTCGACAAGAGCGAAGGCAAGACCATCGCTGTCTATGACCTTGGCGGCGGTACTTTCGACGTGTCGGTTCTGGAAATCGGCGACGGCGTTTTTGAAGTGAAGTCCACCAATGGCGACACGTTCCTTGGCGGTGAAGACTTCGATATTCGTCTGGTCGAATATCTGGTTGCCGAGTTCAAGAAGGAAAGTGGCATCGACCTGAAGAACGACAAGCTTGCCCTGCAGCGCCTCAAGGAAGCTGCCGAAAAGGCCAAGATCGAACTGTCGTCCTCGCAGCAGACCGAAATCAACCTGCCGTTCATCACGGCTGACCAGACTGGCCCGAAGCATCTGGCGATCAAGCTGTCGCGCGCCAAGTTTGAAAGCCTGGTCGATGATCTCGTGCAGCGCACGGTCGAGCCGTGCAAGGCGGCGCTCAAGGATGCCGGCCTCAAGGCTGGCGAAATTGACGAAGTGGTTCTGGTCGGCGGCATGACCCGCATGCCCAAGATTCAGGAAGTCGTGAAGGCCTTCTTCGGCAAGGAACCGCACAAGGGCGTGAACCCGGATGAAGTCGTGGCCATGGGCGCGGCGATCCAGGGCGGCGTTTTGCAGGGCGACGTCAAGGACGTGCTGCTGCTCGACGTGACCCCGCTTTCGCTCGGCATTGAAACGCTGGGCGGCGTGTTCACCCGCCTGATCGAACGCAACACCACTATCCCGACCAAGAAGTCGCAGACCTTCTCCACGGCTGAGGACAACCAGTCGGCCGTGACGATCCGCGTCTTCCAGGGCGAGCGTGAAATGGCAGCCGATAACAAGCTGCTTGGACAGTTCGACCTCGTTGGCATTCCGCCACGTCCCTGCCCGGAAAGCTTGCCGATTGCCAGGAGCGCGATCCGGCCAAGTCCGAAATCTTCATCGTCGAGGGCGATTCGGCAGGCGGTTCCGCCAAGAGCGGGCGCTCGCGCCAGAATCAGGCCATTCTGCCGCTGCGCGGCAAAATCCTGAACGTGGAACGCGTGCGTTTCGACCGGATGATTTCATCCGATCAGGTGGGCACCCTCATCACGGCGCTTGGCACCTCCATCGGCAAGGATGAAACGCACGGCTTCAACGCCGACAAGCTGCGTTATCACAAGATCATCATCATGACCGACGCCGACGTCGATGGCGCCCATATTCGTACGCTTCTGCTCACCTTCTTCTTCCGGCAGATGCCGGAACTGATCGAACGCGGGCATATCTATATCGCGCAGCCGCCGCTCTATAAGGTGACACGCGGCAAGTCTTCGCAATATATCAAGAACGAAGCCGCCTTTGAGGATTTCCTCATCGAAACCGGCCTTGAAGAAACGACACTGGAACTGGTGACTGGCGAAATGCGCGCCGGGCCGGATTTGCGCTCGGTGGTGGAGGATGCGCGCACGCTGCGTCAGCTTCTGCACGGCCTGCACACCCGCTATGACCGCAGCGTGGTGGAACAGGCGGCAATTGCCGGCCTGCTCAACCCCGATGCCTCAAGGGACAATGCAACGGCACAGCATTCCGCCGATACGGTTGCCAAGCGTCTCGACATGATTTCGGAAGAGACCGAGCGCGGCTGGAGCGGCCATGTGATGGAAGACGGCGGCTATCGCTTCGAGCGTATGGTGCGCGGTGTAAAGGATATCGCCATTCTCGACATGGCCCTGCTCGGCTCGGCCGATGCCCGCCAGGTCGACCGAGATCGAGATGTATTCCCGCCTGATCCATACGGTCGATCATATCGAAGGCCGCCTGCGTGACGGCATGGATGCGTTTGACGGCTTCCTCAGCCATGCATGGGCTGTGACGGTGACAGGCGCGCCGAAGCTGTGGGCAATGCGCTTTCTTGAGGAAAACGAACGCAGCCCGCGCGCATGGTATGGCGGCGCGATCGGCATGATGCATTTCAATGGCGATATGAATACAGGGCTGACGCTGCGCACCATCCGCATCAAGGATGGTGTGGCGGAAATCCGTGCAGGGGCGACGCTTCTGTTCGATTCCAACCCTGACGAGGAAGAAGCCGAGACCGAATTGAAGGCATCGGCCATGATTGCGGCTGTGCGGGACGCACAGAAGAGCAATCAGATCGCGGAAGAAAGTGTGGCGGCAAAGGTGGGTGAGGGGGTTTCGATCCTGCTGGTCGATCACGAGGATTCCTTCGTCCATACGCTTGCCAATTATTTCCGCCAGACGGGCGCCAAGGTTTCCACCGTGCGTTCACCGGTGGCAGAGGAGATATTCGACCGCGTCAATCCCGATCTGGTGGTGTTATCGCCGGGACCGGGCTCGCCGCAGGATTTCGATTGCAAGGCGACCATCGATAAGGCGCGCAAGCGCCAGCTTCCGATTTTTGGCGTCTGCCTCGGCCTTCAGGCACTGGCGGAAGCCTATGGCGGGGCGTTGCGCCAGCTTCGCGTTCCGGTGCATGGCAAGCCTTCACGCATCCGCGTATCAAAGCCGGAGCGCATTTTCTCCGGCTTGCCGGAGGAAGTGACGGTGGGGCGTTATCATTCGATCTTCGCCGATCCTGAACGCCTGCCGGATGATTTTCTCGTCACAGCCGAAACGGAAGACGGGATCATAGCCTGCGGTGGAGGTGGTGATGGTGCCGCCGGGCTCCAGCCTGCCTGCGGATGCGGGGCTTGTCGTGTTGCCCGGCACCAAATCCACGATTGCCGATCTGCTGGCGCTGCGTGAAAACGGCTGGGACCGCGAATTGGTCGCCCATGTGAAGCGGGGCGGGCATGTGCTTGGTATTTGCGGCGGGTTTCAAATGCTTGGACGGCGGATCAGTGACCCGGCGGGTATTGAAGGCAATGTGCGCGATATCGAGGGGCTGGGCCTTCTCGATATCGAGACGATGACGGAGCCGGAAAAAGTGGTTCGCAATGTTGAGGCGGTGTCGCTGCTGCATGATGAGCCGCTGGAGGGCTATGAAATCCACATCGGGCGCACCAGCGGGCCGGATATGGCGCGGCCATTTGCGCGTATCGGCGATCATGATGATGGGGCCGTCTCGCCCGATGGTCGTATCATGGGAACCTATCTCCACGGTATTTTCAGTGCGGATCGTTTCCGCCACCACTTTTTGCGCGCGCTGGGTGTGGAAGGCGGCCAGATGAATTATCGCGAGAGCGTCGAAGAGGCTCTGGGCGAACTGGCTGAAGGGCTGGAAGCCTCGCTGGATATTGATGGCCTGTTTGCGCTGGCATGATTGACGCCGCGAAGCCGAAAGCCTAGTGTCAAACCATGTGACAGGTTTTGCCGGAACGAATCCCCGGCAATACCAAAAGGGAATGCGACGGACGGACCCACGCCGGGCGTCTTTATCGCAGCCGACCCCGCGACTGTAGAGCGGAGAGGGAAGAGGCAAGCCGGGCAACCGGCAGCCACTGGAAATCAGATGCGATAATGCAACATCGCATTTTTGCCATCTTCTCGACAGATTATCTCCACACAATGGGGCATTTCGTGCCGCAATTACCCTCGATATGTCACCCCTGTCAGCGCGGCATGGGCGGTTTACTCCCGATGCTGCCCGCCCGATAAGGGACCGCGCAAAACGTAATTTGTGTAAGGAGAATGCCATGCGCACTCTTAAGTCTCTCGTAATCGTCTCGGCTGCGCTGCTGCCGTTCTCTGCGACCGCTTTTGCTGCCGACGCCATCCAGGAACAGCCTCCGGTTCCGGCTCCGGTTGAAGTAGCTCCCCAGTATAGCTGGGCTGGTGGCTATACCGGTCTTTACCTTGGCTATGGCTGGAACAAGGCCAAGACCAGCACCGTTGGCAGCATCAAGCCTGACGATTGGAAGGCTGGCGCCTTTGCTGGCTGGAACTTCCAGCAGGACCAGATCGTATACGGTGTTGAAGGTGATGCAGGTTATTCCTGGGCCAAGAAGTCCAAGGACGGCCTGGAAGTCAAGCAGGGCTTTGAAGGCTCGCTGCGTGCCCGCGTCGGCTACGACCTGAACCCGGTTATGCCGTACCTCACGGCTGGTATTGCCGGTTCGCAGATCAAGCTTAACAACGGCTTGGACGACGAAAGCAAGTTCCGCGTGGGTTGGACGGCTGGTGCCGGTCTCGAAGCCAAGCTGACGGACAACATCCTCGGCCGCGTTGAGTACCGTTACACCCAGTACGGCAACAAGAACTATGATCTGGCCGGTACGACTGTTCGCAACAAGCTGGACACGCAGGATATCCGCGTCGGCATCGGCTACAAGTTCTAATTATAGCATAATTGGACACGGAAAACCGGACAGGCAACTGTCCGGTTTTTTGTTGTCTGCAAAGGTCGAGAAAGCGCGGCAGAGCAACGGCGGCAGCCTGATTTTCAGGGGAAATGAAGTGGAGGCTTCTGTTGCCAGGTGCCTCCGAACCCCGCCTTAAGGGGCTAACCCTAAGGACTTTAGAGTGGGTTTCCCGCACCGCCATTAGGCAGCGAGAGCATAACCCTGAGCATTGTTGTCATTTGCAACTACTCTGTTGACCCGATAACGGTGGTATCATGCCGAGTAAAAGAGCGATCTTTACACCCTTGTCGATCCTGTTTCGCCCCCGCCACAACACAGCCTGATCGGCAAGCTGTGCTGTGGTGGAGGCGCCGGGTACCGCCCCCGGGTCCAATGGGTTTATTACACCGTCCGTTTATCACCATAGTCGGCTTGCGCCGACAGGACGTATATAGGCGTGGTTTTTACCGATTGGAAGGGGGCTTGTGCGTTTTCGCGCAAGACCGACAGAGGTGGTGCGGCCCTTCCGTTCATTTTCCATTGACAGCTTCCGCGTGCTGGTCAATCCTCACAATATATCGGGATCGGCCTTGAAGAGGCTTGGCGCAGCCGGGGCGGAAACCATGGCTGAAACGGGGACGATATGCCCCAATCGAAGGAGAGTGGATATATGAGTGAATATCTCGCGGATGTCCGTCGCTATGATGCTGCCGCCGATGAGGCCGTTGTCGAGAAAATCGTCAAGCATCTTGGCATTGCGCTTCGCAATCGCGATTCCTCGCTCGTTTCGGCAAGC", file=write_ref)
            write_ref.close()

            directory = str(os.getcwd())
            print(directory)
            sample_reference_mlst_location = directory + "/ST1-MLST.fasta"
            read_base = os.path.basename(R1)
            sample_name = re.sub('_.*', '', read_base)
            sample_name_mlst = sample_name + "-mlst"
            print ("mlst reference: %s" % sample_reference_mlst_location)
            ref=re.sub('\.fasta', '', os.path.basename(sample_reference_mlst_location))
            print(ref)

            loc_sam_mlst=directory + "/" + sample_name_mlst
            print ("\n--")
            print("sample name mlst: %s" % sample_name_mlst)
            print("sample reference mlst: %s" % sample_reference_mlst_location)
            print("ref, no ext: %s " % ref)
            print("Read 1: %s" % R1)
            print("Read 2: %s\n" % R2)
            print("directory: %s" % directory)
            print("loc_sam_mlst: %s" % loc_sam_mlst)
            print ("--\n")

            os.system("samtools faidx {}" .format(sample_reference_mlst_location))
            os.system("picard CreateSequenceDictionary REFERENCE={} OUTPUT={}" .format(sample_reference_mlst_location, directory + "/" + ref + ".dict"))
            os.system("bwa index {}" .format(sample_reference_mlst_location))
            
            print("\n@@@ BWA mem")
            samfile_mlst = loc_sam_mlst + ".sam"
            os.system("bwa mem -M -t 16 {} {} {} > {}" .format(sample_reference_mlst_location, R1, R2, samfile_mlst))
            
            print("\nAdd read group and out all BAM")
            all_bam_mlst = loc_sam_mlst + "-all.bam"
            os.system("picard AddOrReplaceReadGroups INPUT={} OUTPUT={} RGLB=lib1 RGPU=unit1 RGSM={} RGPL=illumina" .format(samfile_mlst, all_bam_mlst, sample_name_mlst))

            print("\n@@@ Samtools mapped")
            mapbam = loc_sam_mlst + "-unmapped.bam"
            os.system("samtools view -h -F4 -b -T {} {} -o {}" .format(sample_reference_mlst_location, all_bam_mlst, mapbam))

            print("\n@@@ Sort BAM")
            sortedbam = loc_sam_mlst + "-sorted.bam"
            os.system("samtools sort {} -o {}" .format(mapbam, sortedbam))

            print("\n@@@ Index BAM")
            os.system("samtools index {}" .format(sortedbam))

            print("\n@@@ Calling SNPs with UnifiedGenotyper")
            vcf_mlst = directory + "/" + sample_name + "_mlst" + ".vcf"
            os.system("gatk -R {} -T UnifiedGenotyper -glm BOTH -out_mode EMIT_ALL_SITES -I {} -o {} -nct 8" .format(sample_reference_mlst_location, sortedbam, vcf_mlst))

            # Position 1629 was too close to the end of glk sequence.  Reads would not assemble properly to call possilbe SNP, therefore 100 bases of the gene were added.  Because of this all positions beyond this point are 100 more.  Same with position 1645 and 2693.

            target_vcf_positions = [231, 297, 363, 398, 429, 523, 631, 730, 1247, 1296, 1342, 1381, 1648, 1685, 1741, 1754, 2165, 2224, 2227, 2297, 2300, 2344, 2352, 2403, 2530, 2557, 2578, 2629, 3045, 3054, 3118, 3295, 3328, 3388, 3966, 3969, 4167, 4271, 4296, 4893, 4996, 4998, 5058, 5248, 5672, 5737, 5928, 5963, 5984, 5987, 6025, 6045, 6498, 6499, 6572, 6627, 6715, 6735, 6745, 6785, 6810, 6828, 6845, 6864, 6875, 7382, 7432, 7464, 7594, 7660, 7756]

            pos_call_dict={}
            vcf_reader = vcf.Reader(open(vcf_mlst, 'r'))
            for record in vcf_reader:
                if record.ALT[0]:
                    pos_call_dict.update({record.POS:record.ALT[0]})
                else:
                    pos_call_dict.update({record.POS:record.REF})

            mlst_string=[]
            for i in target_vcf_positions:
                if i in pos_call_dict:
                    mlst_string.append(pos_call_dict[i]) #if number in list then get value
            mlst_join =  ''.join(map(str, mlst_string))
            print(mlst_join)

            mlst_dictionary={}
            mlst_dictionary["CTCCCGGGGCGACCCGATCGAAGCGGGAAGGCCACGGCGCGTGAGCAGCCGGGCATCTGTCCCGCGGGGTA"] = "MLST type 01"
            mlst_dictionary["CTCCCGGGGCGACCCGAGCGAAGCGGGAAGGCCACGGCGCGTGAGCAGCCGGGCATCTGTCCCGCGGGGTA"] = "MLST type 02"
            mlst_dictionary["CTCCCGTGGCGACCCGAGCGAAGCGGGAAGGCCACGGCGCGTGAGCAGCCGGGCATCTGTCCCGCGGGGTA"] = "MLST type 03"
            mlst_dictionary["CTCCCGGGGCGACCCGAGCGAAGCGGGAAGGCCAAGGCGCGTGAGCAGCCGGGCATCTGTCCCGCGGGGTA"] = "MLST type 04"
            mlst_dictionary["CTCCCGGGGCGACCCGATCGAAGCGGGAAGGCCACGGCGAGTGAGCAGCCGGGCATCTGTCCCGCGGGGTA"] = "MLST type 05"
            mlst_dictionary["TTCCTGGGGCAACCCGAGCGAGGCAGGGAGGCCGCGGCTCGTGAGCGGTCGGGCATCTGTCCCGCGGGGTA"] = "MLST type 06"
            mlst_dictionary["CTTCCTGGCCGAGCCGAGTGAAGGGGGGAGGCCACGGCGCGTGCTCGGCTGGGTACCTGTCTCGCGGTGCT"] = "MLST type 07"
            mlst_dictionary["CTTCCTGGCCGACCCGAGTGAAGGGGGGAGGCCACGGCGCGTGCGCGGCTGGGTACCCGTCTCGCGGTGCT"] = "MLST type 08"
            mlst_dictionary["CTTCCTGGCCGACCCGAGTGAAGGGGGGAGGCCACGGCGCGTGCGCGGCTGGGTACCTGTCTCGTGGTGCT"] = "MLST type 09"
            mlst_dictionary["CTTCCTGGCCGACCCGAGTGAAGGGGGGGGGCCACGGCGCGTGCTCGGCTGGGTACCTGTCTCGCGGTGCT"] = "MLST type 10"
            mlst_dictionary["CTTCCTGGCCGACCCGAGTGAAGGGGGGAGGCCACGGCGCGTGCGCGGCTGGGTACCTGTCTCGCGGTGCT"] = "MLST type 11"
            mlst_dictionary["CTTCCTGGCCGACCCGAGTGAAGGGGGGAGGCCACGGCGCGTGCTCGGCTGGGTACCTGTCTCGCGGTGCT"] = "MLST type 12"
            mlst_dictionary["CCCCCGGGCCGACTCGAGCGAAGCGAAGAGGCCACGGCGCGTGAGTGACCAGGCACCTATCCCACGGGGTA"] = "MLST type 13"
            mlst_dictionary["CCCCCGGGCCGGCCCAAGCGAAGCGGGGAGGCTACAGTGCGTGAGTGGCCAGGCACCTGTCCCGCGGGGTA"] = "MLST type 14"
            mlst_dictionary["CCCCCGGGCCGACCCGGGCGAAGCGGGGAGGCTACGGTGCGTGAGTGGCCAGGCACCTGTCCCGCGAGGTA"] = "MLST type 15"
            mlst_dictionary["CCCCCGGCCCGACCCGGGCGAAGCGGGGAGGCTACGGTGCGTGAGTGGCCAGGCACCTGTCCCGCGAGGTA"] = "MLST type 16"
            mlst_dictionary["CCCCCGGGCCGGCCCAAGCGAAGCGGGGAGGCTACAATGCGTGAGTGGCCAGGCACCTGTCCCGCAGGGTA"] = "MLST type 17"
            mlst_dictionary["CCCCCGGGCCGGCCCAAGCGAAGCGGGGAGGCTACAATGCGTGAGTGGCCAGGCACCTGTCCCGCAGGCTA"] = "MLST type 18"
            mlst_dictionary["CCCCCGGGCCGACCCGAGCGAAGCGGGGAGGACACGGCGCGTGAGTGGCCAGGCACCTGTCCCGCGGGGTA"] = "MLST type 19"
            mlst_dictionary["CCCCCGGGCCGGCCCAAGCGAAGCGGGGAGGCTACAATGCGTGAGTGGCCAGGCACATGTCCCGCAGGGTA"] = "MLST type 20"
            mlst_dictionary["CCCCCGGGCCGGCCCAAGCGAAGCGGGGAGGCTACAATGCGTGAGTGGCCAGGCACATGCCCCGCAGGGTA"] = "MLST type 21"
            mlst_dictionary["CCCCCGGGCCGACCCGAGCGAGGCGGGGAGGCCACGGCGCGGGAGTGGCCAGACACCTGTCCTGCGGGGTA"] = "MLST type 22"
            mlst_dictionary["CCCCCGGGCTGACCCGAGCGAAACGGGGAAGCCACGGCGCGTAAGTGGCCAGGCACCTGTCCCGCGGGGTA"] = "MLST type 23"
            mlst_dictionary["CCCCCGGGCTGACCCGAGCGGAACGGGGAAGCCACGGCGCGTAAGTGGCCAGGCACCTGTCCCGCGGGGTA"] = "MLST type 23x"
            mlst_dictionary["CCCCCGGGCCGACCCGAGCAAAGCGGGGAGGCCACGGCGCGTAAGTGGCCAGGCACCTGTCCCGCGGGGTA"] = "MLST type 24"
            mlst_dictionary["CCCCCGGGCCGACCCGAGCGAAGCGGGGAGGCCACGGCGCGTAAGTGGCCAGGCACCTGTCCCGCGGGGTA"] = "MLST type 25"
            mlst_dictionary["CCCCCGGGCCGACCCGAGCGAAGCGGGGAGGCCACGGCGCGTAAGTGGCCAAGCACCTGTTCCGCGGGGTA"] = "MLST type 26"
            mlst_dictionary["CCCCCGGGCCGACCCGAGCGAAGCGGGGAGACCACGGCGCATAAGTGGCCAGGCACCTGTCCCGCGGGGTA"] = "MLST type 27"
            mlst_dictionary["CCCTCGGGCCGACCTGAGCGAAGCGGGGAGACCACGGCGCATAAGTGGCCAGGCTCCTGTCCCGCGGGGTA"] = "MLST type 28"

            for i in fastqs: #remove unzipped fastq files to save space
                os.remove(i)

            remove_files = glob.glob('ST1-MLST*')
            for i in remove_files:
                os.remove(i)
            remove_files = glob.glob('*-mlst*')
            for i in remove_files:
                os.remove(i)
            remove_files = glob.glob('*_mlst.vcf.idx')
            for i in remove_files:
                os.remove(i)

            write_out = open("mlst.txt", 'w')
            
            if mlst_join in mlst_dictionary:
                mlst_type = mlst_dictionary[mlst_join]
                print(mlst_type)
                print(mlst_type, file=write_out)
            else:
                print("NO MLST MATCH FOUND\n")
                print("NO MLST MATCH FOUND", file=write_out)
            
            write_out.close()

        def finding_sp(v):
            total=0
            total_finds=0
            for fastq in R1unzip, R2unzip:
                with open(fastq) as in_handle:
                    # all 3, title and seq and qual, were needed
                    for title, seq, qual in FastqGeneralIterator(in_handle):
                        #if total < 6: # doesn't make a big different.  Might as well get full counts
    #                    total += sum(seq.count(x) for x in (v)) #v=list of for and rev spacer
                        for spacer in v:
                            total_finds = len(regex.findall("(" + spacer + "){s<=1}", seq, overlapped=True))
                            total += total_finds
            return(v, total)

        def binary_to_octal(binary):
            binary_len = len(binary)
            i = 0
            ie = 1
            octal = ""
            while ie < 43:
                ie = i + 3
                print(binary[i:ie])
                region = binary[i:ie]
                region_len = len(region)
                i += 3
                if int(region[0]) == 1:
                    if region_len < 2: # for the lone spacer 43.  When present needs to be 1 not 4.
                        oct = 1
                    else:
                        oct = 4
                else:
                    oct = 0
                try:
                    if int(region[1]) == 1:
                        oct += 2
                    if int(region[2]) == 1:
                        oct += 1
                except IndexError:
                    pass
                octal = octal + str(oct)
            return(octal)

        def binary_to_hex(binary):
            section1 = binary[0:7]
            section2 = binary[7:14]
            section3 = binary[14:21]
            section4 = binary[21:28]
            section5 = binary[28:36]
            section6 = binary[36:43]

            hex_section1 = hex(int(section1, 2))
            hex_section2 = hex(int(section2, 2))
            hex_section3 = hex(int(section3, 2))
            hex_section4 = hex(int(section4, 2))
            hex_section5 = hex(int(section5, 2))
            hex_section6 = hex(int(section6, 2))

            return(hex_section1.replace('0x', '').upper() + "-" + hex_section2.replace('0x', '').upper() + "-" + hex_section3.replace('0x', '').upper() + "-" + hex_section4.replace('0x', '').upper() + "-" + hex_section5.replace('0x', '').upper() + "-" + hex_section6.replace('0x', '').upper())

        def spoligo(self):
            
            print("\nFinding spoligotype pattern...\n")
            
            fastqs = glob.glob(zips + '/*.fastq')
            if len(fastqs) < 2:
                script1.unzipfiles()
            fastqs = glob.glob(zips + '/*.fastq')
          
            '''spoligo spacers'''
            spoligo_dictionary = {}
            spoligo_dictionary["spacer01"] = ["TGATCCAGAGCCGGCGACCCTCTAT", "ATAGAGGGTCGCCGGCTCTGGATCA"]
            spoligo_dictionary["spacer02"] = ["CAAAAGCTGTCGCCCAAGCATGAGG", "CCTCATGCTTGGGCGACAGCTTTTG"]
            spoligo_dictionary["spacer03"] = ["CCGTGCTTCCAGTGATCGCCTTCTA", "TAGAAGGCGATCACTGGAAGCACGG"]
            spoligo_dictionary["spacer04"] = ["ACGTCATACGCCGACCAATCATCAG", "CTGATGATTGGTCGGCGTATGACGT"]
            spoligo_dictionary["spacer05"] = ["TTTTCTGACCACTTGTGCGGGATTA", "TAATCCCGCACAAGTGGTCAGAAAA"]
            spoligo_dictionary["spacer06"] = ["CGTCGTCATTTCCGGCTTCAATTTC", "GAAATTGAAGCCGGAAATGACGACG"]
            spoligo_dictionary["spacer07"] = ["GAGGAGAGCGAGTACTCGGGGCTGC", "GCAGCCCCGAGTACTCGCTCTCCTC"]
            spoligo_dictionary["spacer08"] = ["CGTGAAACCGCCCCCAGCCTCGCCG", "CGGCGAGGCTGGGGGCGGTTTCACG"]
            spoligo_dictionary["spacer09"] = ["ACTCGGAATCCCATGTGCTGACAGC", "GCTGTCAGCACATGGGATTCCGAGT"]
            spoligo_dictionary["spacer10"] = ["TCGACACCCGCTCTAGTTGACTTCC", "GGAAGTCAACTAGAGCGGGTGTCGA"]
            spoligo_dictionary["spacer11"] = ["GTGAGCAACGGCGGCGGCAACCTGG", "CCAGGTTGCCGCCGCCGTTGCTCAC"]
            spoligo_dictionary["spacer12"] = ["ATATCTGCTGCCCGCCCGGGGAGAT", "ATCTCCCCGGGCGGGCAGCAGATAT"]
            spoligo_dictionary["spacer13"] = ["GACCATCATTGCCATTCCCTCTCCC", "GGGAGAGGGAATGGCAATGATGGTC"]
            spoligo_dictionary["spacer14"] = ["GGTGTGATGCGGATGGTCGGCTCGG", "CCGAGCCGACCATCCGCATCACACC"]
            spoligo_dictionary["spacer15"] = ["CTTGAATAACGCGCAGTGAATTTCG", "CGAAATTCACTGCGCGTTATTCAAG"]
            spoligo_dictionary["spacer16"] = ["CGAGTTCCCGTCAGCGTCGTAAATC", "GATTTACGACGCTGACGGGAACTCG"]
            spoligo_dictionary["spacer17"] = ["GCGCCGGCCCGCGCGGATGACTCCG", "CGGAGTCATCCGCGCGGGCCGGCGC"]
            spoligo_dictionary["spacer18"] = ["CATGGACCCGGGCGAGCTGCAGATG", "CATCTGCAGCTCGCCCGGGTCCATG"]
            spoligo_dictionary["spacer19"] = ["TAACTGGCTTGGCGCTGATCCTGGT", "ACCAGGATCAGCGCCAAGCCAGTTA"]
            spoligo_dictionary["spacer20"] = ["TTGACCTCGCCAGGAGAGAAGATCA", "TGATCTTCTCTCCTGGCGAGGTCAA"]
            spoligo_dictionary["spacer21"] = ["TCGATGTCGATGTCCCAATCGTCGA", "TCGACGATTGGGACATCGACATCGA"]
            spoligo_dictionary["spacer22"] = ["ACCGCAGACGGCACGATTGAGACAA", "TTGTCTCAATCGTGCCGTCTGCGGT"]
            spoligo_dictionary["spacer23"] = ["AGCATCGCTGATGCGGTCCAGCTCG", "CGAGCTGGACCGCATCAGCGATGCT"]
            spoligo_dictionary["spacer24"] = ["CCGCCTGCTGGGTGAGACGTGCTCG", "CGAGCACGTCTCACCCAGCAGGCGG"]
            spoligo_dictionary["spacer25"] = ["GATCAGCGACCACCGCACCCTGTCA", "TGACAGGGTGCGGTGGTCGCTGATC"]
            spoligo_dictionary["spacer26"] = ["CTTCAGCACCACCATCATCCGGCGC", "GCGCCGGATGATGGTGGTGCTGAAG"]
            spoligo_dictionary["spacer27"] = ["GGATTCGTGATCTCTTCCCGCGGAT", "ATCCGCGGGAAGAGATCACGAATCC"]
            spoligo_dictionary["spacer28"] = ["TGCCCCGGCGTTTAGCGATCACAAC", "GTTGTGATCGCTAAACGCCGGGGCA"]
            spoligo_dictionary["spacer29"] = ["AAATACAGGCTCCACGACACGACCA", "TGGTCGTGTCGTGGAGCCTGTATTT"]
            spoligo_dictionary["spacer30"] = ["GGTTGCCCCGCGCCCTTTTCCAGCC", "GGCTGGAAAAGGGCGCGGGGCAACC"]
            spoligo_dictionary["spacer31"] = ["TCAGACAGGTTCGCGTCGATCAAGT", "ACTTGATCGACGCGAACCTGTCTGA"]
            spoligo_dictionary["spacer32"] = ["GACCAAATAGGTATCGGCGTGTTCA", "TGAACACGCCGATACCTATTTGGTC"]
            spoligo_dictionary["spacer33"] = ["GACATGACGGCGGTGCCGCACTTGA", "TCAAGTGCGGCACCGCCGTCATGTC"]
            spoligo_dictionary["spacer34"] = ["AAGTCACCTCGCCCACACCGTCGAA", "TTCGACGGTGTGGGCGAGGTGACTT"]
            spoligo_dictionary["spacer35"] = ["TCCGTACGCTCGAAACGCTTCCAAC", "GTTGGAAGCGTTTCGAGCGTACGGA"]
            spoligo_dictionary["spacer36"] = ["CGAAATCCAGCACCACATCCGCAGC", "GCTGCGGATGTGGTGCTGGATTTCG"]
            spoligo_dictionary["spacer37"] = ["CGCGAACTCGTCCACAGTCCCCCTT", "AAGGGGGACTGTGGACGAGTTCGCG"]
            spoligo_dictionary["spacer38"] = ["CGTGGATGGCGGATGCGTTGTGCGC", "GCGCACAACGCATCCGCCATCCACG"]
            spoligo_dictionary["spacer39"] = ["GACGATGGCCAGTAAATCGGCGTGG", "CCACGCCGATTTACTGGCCATCGTC"]
            spoligo_dictionary["spacer40"] = ["CGCCATCTGTGCCTCATACAGGTCC", "GGACCTGTATGAGGCACAGATGGCG"]
            spoligo_dictionary["spacer41"] = ["GGAGCTTTCCGGCTTCTATCAGGTA", "TACCTGATAGAAGCCGGAAAGCTCC"]
            spoligo_dictionary["spacer42"] = ["ATGGTGGGACATGGACGAGCGCGAC", "GTCGCGCTCGTCCATGTCCCACCAT"]
            spoligo_dictionary["spacer43"] = ["CGCAGAATCGCACCGGGTGCGGGAG", "CTCCCGCACCCGGTGCGATTCTGCG"]

    #        spoligo_dictionary["spacer01"] = ["TGATCCAGAGCCGGCGACCCTCTAT"]
    #        spoligo_dictionary["spacer02"] = ["CAAAAGCTGTCGCCCAAGCATGAGG"]
    #        spoligo_dictionary["spacer03"] = ["CCGTGCTTCCAGTGATCGCCTTCTA"]
    #        spoligo_dictionary["spacer04"] = ["ACGTCATACGCCGACCAATCATCAG"]
    #        spoligo_dictionary["spacer05"] = ["TTTTCTGACCACTTGTGCGGGATTA"]
    #        spoligo_dictionary["spacer06"] = ["CGTCGTCATTTCCGGCTTCAATTTC"]
    #        spoligo_dictionary["spacer07"] = ["GAGGAGAGCGAGTACTCGGGGCTGC"]
    #        spoligo_dictionary["spacer08"] = ["CGTGAAACCGCCCCCAGCCTCGCCG"]
    #        spoligo_dictionary["spacer09"] = ["ACTCGGAATCCCATGTGCTGACAGC"]
    #        spoligo_dictionary["spacer10"] = ["TCGACACCCGCTCTAGTTGACTTCC"]
    #        spoligo_dictionary["spacer11"] = ["GTGAGCAACGGCGGCGGCAACCTGG"]
    #        spoligo_dictionary["spacer12"] = ["ATATCTGCTGCCCGCCCGGGGAGAT"]
    #        spoligo_dictionary["spacer13"] = ["GACCATCATTGCCATTCCCTCTCCC"]
    #        spoligo_dictionary["spacer14"] = ["GGTGTGATGCGGATGGTCGGCTCGG"]
    #        spoligo_dictionary["spacer15"] = ["CTTGAATAACGCGCAGTGAATTTCG"]
    #        spoligo_dictionary["spacer16"] = ["CGAGTTCCCGTCAGCGTCGTAAATC"]
    #        spoligo_dictionary["spacer17"] = ["GCGCCGGCCCGCGCGGATGACTCCG"]
    #        spoligo_dictionary["spacer18"] = ["CATGGACCCGGGCGAGCTGCAGATG"]
    #        spoligo_dictionary["spacer19"] = ["TAACTGGCTTGGCGCTGATCCTGGT"]
    #        spoligo_dictionary["spacer20"] = ["TTGACCTCGCCAGGAGAGAAGATCA"]
    #        spoligo_dictionary["spacer21"] = ["TCGATGTCGATGTCCCAATCGTCGA"]
    #        spoligo_dictionary["spacer22"] = ["ACCGCAGACGGCACGATTGAGACAA"]
    #        spoligo_dictionary["spacer23"] = ["AGCATCGCTGATGCGGTCCAGCTCG"]
    #        spoligo_dictionary["spacer24"] = ["CCGCCTGCTGGGTGAGACGTGCTCG"]
    #        spoligo_dictionary["spacer25"] = ["GATCAGCGACCACCGCACCCTGTCA"]
    #        spoligo_dictionary["spacer26"] = ["CTTCAGCACCACCATCATCCGGCGC"]
    #        spoligo_dictionary["spacer27"] = ["GGATTCGTGATCTCTTCCCGCGGAT"]
    #        spoligo_dictionary["spacer28"] = ["TGCCCCGGCGTTTAGCGATCACAAC"]
    #        spoligo_dictionary["spacer29"] = ["AAATACAGGCTCCACGACACGACCA"]
    #        spoligo_dictionary["spacer30"] = ["GGTTGCCCCGCGCCCTTTTCCAGCC"]
    #        spoligo_dictionary["spacer31"] = ["TCAGACAGGTTCGCGTCGATCAAGT"]
    #        spoligo_dictionary["spacer32"] = ["GACCAAATAGGTATCGGCGTGTTCA"]
    #        spoligo_dictionary["spacer33"] = ["GACATGACGGCGGTGCCGCACTTGA"]
    #        spoligo_dictionary["spacer34"] = ["AAGTCACCTCGCCCACACCGTCGAA"]
    #        spoligo_dictionary["spacer35"] = ["TCCGTACGCTCGAAACGCTTCCAAC"]
    #        spoligo_dictionary["spacer36"] = ["CGAAATCCAGCACCACATCCGCAGC"]
    #        spoligo_dictionary["spacer37"] = ["CGCGAACTCGTCCACAGTCCCCCTT"]
    #        spoligo_dictionary["spacer38"] = ["CGTGGATGGCGGATGCGTTGTGCGC"]
    #        spoligo_dictionary["spacer39"] = ["GACGATGGCCAGTAAATCGGCGTGG"]
    #        spoligo_dictionary["spacer40"] = ["CGCCATCTGTGCCTCATACAGGTCC"]
    #        spoligo_dictionary["spacer41"] = ["GGAGCTTTCCGGCTTCTATCAGGTA"]
    #        spoligo_dictionary["spacer42"] = ["ATGGTGGGACATGGACGAGCGCGAC"]
    #        spoligo_dictionary["spacer43"] = ["CGCAGAATCGCACCGGGTGCGGGAG"]

            count_summary={}

            with futures.ProcessPoolExecutor() as pool: #max_workers=4
                for v, count in pool.map(script1.finding_sp, spoligo_dictionary.values()):
                    for k, value in spoligo_dictionary.items():
                        if v == value:
                            count_summary.update({k:count})
                            count_summary=OrderedDict(sorted(count_summary.items()))

    #        for v in spoligo_dictionary.values():
    #            v, count = script1.finding_sp(v)
    #            print(v)
    #            print(total)
    #            for k, value in spoligo_dictionary.items():
    #                if v == value:
    #                    count_summary.update({k:count})
    #                    count_summary=OrderedDict(sorted(count_summary.items()))

            #Binary dictionary
            spoligo_binary_dictionary={}
            for k, v in count_summary.items():
                if v > 4:
                    spoligo_binary_dictionary.update({k:1})
                else:
                    spoligo_binary_dictionary.update({k:0})
            spoligo_binary_dictionary=OrderedDict(sorted(spoligo_binary_dictionary.items()))
            
            spoligo_binary_list=[]
            for v in spoligo_binary_dictionary.values():
                spoligo_binary_list.append(v)
            bovis_string=''.join(str(e) for e in spoligo_binary_list) #bovis_string correct
            hexadecimal = script1.binary_to_hex(bovis_string)
            
            write_out = open("spoligo.txt", 'w')
            
            found = False
            with open(spoligo_db) as f: # put into dictionary or list
                for line in f:
                    line=line.rstrip()
                    octalcode = line.split()[0] #no arg splits on whitespace
                    sbcode = line.split()[1]
                    binarycode = line.split()[2]
                    if bovis_string == '0000000000000000000000000000000000000000000':
                        found=True
                        print("%s %s %s %s" % (octalcode, sbcode, hexadecimal, binarycode))
                        print("%s %s %s %s" % (octalcode, sbcode, hexadecimal, binarycode), file=write_out)
                        print("CHECK SAMPLE!  NO SPACERS FOUND.  LIKELY NOT TB COMPLEX.  ALTHOUGH SB2277 IS A ZERO STRING BINARY\n")
                        print("CHECK SAMPLE!  NO SPACERS FOUND.  LIKELY NOT TB COMPLEX.  ALTHOUGH SB2277 IS A ZERO STRING BINARY", file=write_out)
                        print("\nOne mismatch allowed spacers search against both R1 and R2 reads.\n", file=write_out)
                        for k, v in count_summary.items():
                            print(k, v, file=write_out)
                    elif bovis_string == binarycode:
                        found=True
                        print("Pattern found:")
                        print("%s %s %s %s" % (octalcode, sbcode, hexadecimal, binarycode))
                        print("%s %s %s %s" % (octalcode, sbcode, hexadecimal, binarycode), file=write_out)
                        print("\One mismatch allowed spacer search against both R1 and R2 reads.\n", file=write_out)
                        for k, v in count_summary.items():
                            print(k, v, file=write_out)
            if not found:
                octal = script1.binary_to_octal(bovis_string)
                sbcode = "N/A"
                print("%s %s %s %s" % (octal, sbcode, hexadecimal, bovis_string))
                print("%s %s %s %s" % (octal, sbcode, hexadecimal, bovis_string), file=write_out)
                print("SPOLIGO SB NUMBER NOT FOUND\n")
                print("\nSPOLIGO SB NUMBER NOT FOUND\n", file=write_out)
                print("\nOne mismatch allowed spacer search against both R1 and R2 reads.\n", file=write_out)
                
                for k, v in count_summary.items():
                    print(k, v, file=write_out)

            print("bovis_string: %s" % bovis_string, file=write_out)
            print("binarycode  : %s" % binarycode, file=write_out)

            for i in fastqs: #remove unzipped fastq files to save space
                os.remove(i)
                
            write_out.close()

        def best_reference(self):
        
            '''Use oligos to determine species.  Most often if the absents of a single oligo from a set specific for either brucella or bovis will confer species type.  Some species will the absents of more than one oligo.  Oligo findings are translated to binary patterns.'''
            
            fastqs = glob.glob(zips + '/*.fastq')
            if len(fastqs) < 2:
                script1.unzipfiles()
            fastqs = glob.glob(zips + '/*.fastq')

            print("\nFinding the best reference\n")
            
            write_out = open("best_reference.txt", 'w')
          
            '''get the species'''
            oligo_dictionary = {}
            oligo_dictionary["01_ab1"] = "AATTGTCGGATAGCCTGGCGATAACGACGC"
            oligo_dictionary["02_ab3"] = "CACACGCGGGCCGGAACTGCCGCAAATGAC"
            oligo_dictionary["03_ab5"] = "GCTGAAGCGGCAGACCGGCAGAACGAATAT"
            oligo_dictionary["04_mel"] = "TGTCGCGCGTCAAGCGGCGTGAAATCTCTG"
            oligo_dictionary["05_suis1"] = "TGCGTTGCCGTGAAGCTTAATTCGGCTGAT"
            oligo_dictionary["06_suis2"] = "GGCAATCATGCGCAGGGCTTTGCATTCGTC"
            oligo_dictionary["07_suis3"] = "CAAGGCAGATGCACATAATCCGGCGACCCG"
            oligo_dictionary["08_ceti1"] = "GTGAATATAGGGTGAATTGATCTTCAGCCG"
            oligo_dictionary["09_ceti2"] = "TTACAAGCAGGCCTATGAGCGCGGCGTGAA"
            oligo_dictionary["10_canis4"] = "CTGCTACATAAAGCACCCGGCGACCGAGTT"
            oligo_dictionary["11_canis"] = "ATCGTTTTGCGGCATATCGCTGACCACAGC"
            oligo_dictionary["12_ovis"] = "CACTCAATCTTCTCTACGGGCGTGGTATCC"
            oligo_dictionary["13_ether2"] = "CGAAATCGTGGTGAAGGACGGGACCGAACC"
            oligo_dictionary["14_63B1"] = "CCTGTTTAAAAGAATCGTCGGAACCGCTCT"
            oligo_dictionary["15_16M0"] = "TCCCGCCGCCATGCCGCCGAAAGTCGCCGT"
            oligo_dictionary["16_tb157"] = "CTCTTCGTATACCGTTCCGTCGTCACCATGGTCCT"
            oligo_dictionary["17_tb7"] = "TCACGCAGCCAACGATATTCGTGTACCGCGACGGT"
            oligo_dictionary["18_tbbov"] = "CTGGGCGACCCGGCCGACCTGCACACCGCGCATCA"
            oligo_dictionary["19_tb5"] = "CCGTGGTGGCGTATCGGGCCCCTGGATCGCGCCCT"
            oligo_dictionary["20_tb2"] = "ATGTCTGCGTAAAGAAGTTCCATGTCCGGGAAGTA"
            oligo_dictionary["21_tb3"] = "GAAGACCTTGATGCCGATCTGGGTGTCGATCTTGA"
            oligo_dictionary["22_tb4"] = "CGGTGTTGAAGGGTCCCCCGTTCCAGAAGCCGGTG"
            oligo_dictionary["23_tb6"] = "ACGGTGATTCGGGTGGTCGACACCGATGGTTCAGA"
            oligo_dictionary["24_para"] = "CCTTTCTTGAAGGGTGTTCG"
            oligo_dictionary["25_para2"] = "CGAACACCCTTCAAGAAAGG"

            brucella_identifications = {}
            brucella_identifications["111111111111111"] = "odd" #Unexpected findings
            brucella_identifications["011111111111111"] = "ab1" #Brucella abortus bv 1, 2 or 4
            brucella_identifications["101111111111111"] = "ab3" #Brucella abortus bv 3
            brucella_identifications["110111111111111"] = "ab1" #Brucella abortus bv 5, 6 or 9
            brucella_identifications["111011111111110"] = "mel1"
            brucella_identifications["000001010110110"] = "mel1"
            brucella_identifications["111011111111101"] = "mel2"
            brucella_identifications["000001010110100"] = "mel2"
            brucella_identifications["010001010110100"] = "mel2"
            brucella_identifications["111001111110101"] = "mel2"
            brucella_identifications["111011111111011"] = "mel3"
            brucella_identifications["111001111110011"] = "mel3"
            brucella_identifications["111101111111111"] = "suis1"
            brucella_identifications["111110111111111"] = "suis2"
            brucella_identifications["111111011111110"] = "suis3"
            brucella_identifications["111111101111111"] = "ceti1"
            brucella_identifications["111111100111111"] = "ceti1"
            brucella_identifications["111111110111111"] = "ceti2"
            brucella_identifications["111111111011110"] = "suis4"
            brucella_identifications["111111111001110"] = "canis"
            brucella_identifications["111111111110111"] = "ovis"

            bovis_identifications = {}
            bovis_identifications["11101111"] = "h37" #tb1
            bovis_identifications["11101101"] = "h37" #tb1
            bovis_identifications["01100111"] = "h37" #tb2
            bovis_identifications["01101011"] = "h37" #tb3
            bovis_identifications["11101011"] = "h37" #tb3
            bovis_identifications["01101111"] = "h37" #tb4a
            bovis_identifications["01101101"] = "h37" #tb4b
            bovis_identifications["11101101"] = "h37" #tb4b
            bovis_identifications["01101111"] = "h37" #tb4b
            bovis_identifications["11111111"] = "h37" #tb5
            bovis_identifications["11001111"] = "h37" #tb6
            bovis_identifications["10101110"] = "h37" #tb7
            bovis_identifications["11001110"] = "bovis" #bovis
            bovis_identifications["11011110"] = "bovis" #bovis
            bovis_identifications["11001100"] = "bovis" #bovis
            
            para_identifications = {}
            para_identifications["1"] = "para"
            para_identifications["01"] = "para"
            para_identifications["11"] = "para"

            count_summary={}

            with futures.ProcessPoolExecutor() as pool: #max_workers=4
                for v, count in pool.map(script1.finding_best_ref, oligo_dictionary.values()):
                    for k, value in oligo_dictionary.items():
                        if v == value:
                            count_summary.update({k:count})
                            count_summary=OrderedDict(sorted(count_summary.items()))

            count_list=[]
            for v in count_summary.values():
                count_list.append(v)
            brucella_sum=sum(count_list[:15])
            bovis_sum=sum(count_list[15:23])
            para_sum=sum(count_list[23:])
            
            print("Best reference Brucella counts:", file=write_out)
            for i in count_list[:15]:
                print(i,  end=',', file=write_out)
                
            print("\nBest reference TB counts:", file=write_out)
            for i in count_list[15:23]:
                print(i,  end=',', file=write_out)

            print("\nBest reference Para counts:", file=write_out)
            for i in count_list[23:]:
                print(i,  end=',', file=write_out)

            #Binary dictionary
            binary_dictionary={}
            for k, v in count_summary.items():
                if v > 1:
                    binary_dictionary.update({k:1})
                else:
                    binary_dictionary.update({k:0})
            binary_dictionary=OrderedDict(sorted(binary_dictionary.items()))

            binary_list=[]
            for v in binary_dictionary.values():
                binary_list.append(v)
            brucella_binary=binary_list[:15]
            brucella_string=''.join(str(e) for e in brucella_binary)
            bovis_binary=binary_list[15:23]
            bovis_string=''.join(str(e) for e in bovis_binary)
            para_binary=binary_list[23:]
            para_string=''.join(str(e) for e in para_binary)

            if brucella_sum > 3:
                if brucella_string in brucella_identifications:
                    print("Brucella group, species %s" % brucella_identifications[brucella_string])
                    print("\n\nBrucella group, species %s" % brucella_identifications[brucella_string], file=write_out)
                    return(brucella_identifications[brucella_string]) # return to set parameters
                else:
                    print("Brucella group, but no match")
                    print("\n\nBrucella group, but no match", file=write_out)
            elif bovis_sum > 3:
                if bovis_string in bovis_identifications:
                    print("TB group, species %s" % bovis_identifications[bovis_string])
                    print("\n\nTB group, species %s" % bovis_identifications[bovis_string], file=write_out)
                    return(bovis_identifications[bovis_string]) # return to set parameters
                else:
                    print("TB group, but no match")
                    print("\n\nTB group, but no match", file=write_out)
            elif para_sum >= 1:
                if para_string in para_identifications:
                    print("Para group")
                    print("\n\nPara group", file=write_out)
                    return("para") # return to set parameters
                else:
                    print("No match")
                    print("\n\nNo match", file=write_out)

            write_out.close()
            
            for i in fastqs: #remove unzipped fastq files to save space
                os.remove(i)

        def add_zero_coverage(coverage_in, vcf_file, loc_sam):
            
            temp_vcf = loc_sam + "-temp.vcf"
            zero_coverage_vcf = loc_sam + "_zc.vcf"
            
            zero_position=[]
            total_length = 0
            total_zero_coverage = 0
            with open(coverage_in) as f:
                for line in f:
                    total_length = total_length + 1
                    line.rstrip()
                    line=re.split(':|\t', line)
                    chromosome=line[0]
                    position=line[1]
                    abs_pos = chromosome + "-" + position
                    depth=line[2]
                    if depth == "0":
                        zero_position.append(abs_pos) #positions with zero coverage in coverage file
                        total_zero_coverage = total_zero_coverage + 1
                print(len(zero_position))
            
            genome_coverage = 0
            total_coverage = total_length - total_zero_coverage

            genome_coverage =  "{:.2%}".format(total_coverage/total_length)

            average_list = []
            with open(coverage_in) as f:
                for line in f:
                    line.rstrip()
                    line=re.split(':|\t', line)
                    depth=str(line[2])
                    if depth.isdigit():
                        depth = int(depth)
                        average_list.append(depth)
                ave_coverage = mean(average_list)

            zero_position_found=[]
            write_out=open(temp_vcf, 'w')
            with open(vcf_file) as f:
                for line in f:
                    line=line.rstrip()
                    if line.startswith("#"): # save headers to file
                        print(line, file=write_out)
                    elif not line.startswith("#"): # position rows
                        split_line = line.split('\t')
                        chromosome=split_line[0] # get chromosome
                        position=split_line[1] # get position
                        abs_pos = chromosome + "-" + position
                        ref=split_line[3] # REF
                        alt=split_line[4] # ALT
                        ref_len=len(ref)
                        alt_len=len(alt)
                        if abs_pos in zero_position: # if a position has zero coverage
                            print("%s is in zeropostions" % position)
                            zero_position_found.append(position)
                            print("%s\t%s\t.\tN\t.\t.\t.\t.\tGT\t./." % (chromosome, position), file=write_out) # print a zero coverage line
                        elif ref_len == 1 and alt_len == 1:
                            print(line, file=write_out)
                print("##### Chromosome: %s" % chromosome)
                #zero_position = list(map(int, zero_position)) # change list items from string to numbers
                #zero_position_found = list(map(int, zero_position_found))

                print("using list comprehension")
                zero_not_added = [x for x in zero_position if x not in  zero_position_found] # use list comprehension to subtract one list from the other
                for abs_position in zero_not_added:
                    split_line = abs_position.split('-')
                    chromosome=split_line[0]
                    position=split_line[1]
                    print("%s\t%s\t.\tN\t.\t.\t.\t.\tGT\t./." % (chromosome, position), file=write_out) # print a zero coverage line
            write_out.close()

            os.system("picard SortVcf INPUT={} OUTPUT={}" .format(temp_vcf, zero_coverage_vcf))
            #os.system("vcf-sort {} > {}" .format(temp_vcf, zero_coverage_vcf))
            os.remove(temp_vcf)
            
            vcf_reader = vcf.Reader(open(zero_coverage_vcf, 'r'))
            good_snp_count = 0
            for record in vcf_reader:
                try:
                    chrom = record.CHROM
                    position = record.POS
                    try:
                        if str(record.ALT[0]) != "None" and record.INFO['AC'][0] == 2 and len(record.REF) == 1 and record.QUAL > 150:
                            good_snp_count = good_snp_count + 1
                    except KeyError:
                        pass
                except ZeroDivisionError:
                    print ("ZeroDivisionError error found")
                except ValueError:
                    print ("ValueError error found")
                except UnboundLocalError:
                    print ("UnboundLocalError error found")
                except TypeError:
                    print ("TypeError error found")

            return(zero_coverage_vcf, good_snp_count, ave_coverage, genome_coverage)

        def align_reads(self):
        
            if self.species == "NO FINDINGS":
                read_base = os.path.basename(R1)
                sample_name=re.sub('_.*', '', read_base)
                R1size = script1.sizeof_fmt(os.path.getsize(R1))
                R2size = script1.sizeof_fmt(os.path.getsize(R2))
                stat_summary = {}
                stat_summary["01"] = sample_name
                stat_summary["02"] = "NOT_FOUND"
                stat_summary["03"] = "N/A"
                stat_summary["04"] = R1size
                stat_summary["05"] = R2size
                stat_summary["06"] = "CHECK SAMPLE *****************************************"
                stat_summary=OrderedDict(sorted(stat_summary.items()))
                return(stat_summary)
            else:
                startTime = datetime.now()
                print ("\n\n*** START ***\n")
                print ("Start time: %s" % startTime)

                read_base = os.path.basename(R1)
                sample_name=re.sub('_.*', '', read_base)

                sample_reference=glob.glob(directory + '/*fasta')
                hqs=glob.glob(directory + '/*vcf')
                
                print("self.species: %s" % self.species)
                if self.species in ["ab1", "ab3", "suis1", "suis3", "suis4", "mel1", "mel2", "mel3", "canis", "ceti1", "ceti2"]:
                    print("Brucella")
                    self.mlst()
                elif self.species in ["bovis", "h37", "af"]:
                    print("TB")
                    self.spoligo()
                
                print ("reference: %s" % sample_reference)
                ref=re.sub('\.fasta', '', os.path.basename(sample_reference[0]))
                if len(sample_reference) != 1:
                    print("### ERROR reference not available or too many")
                    sys.exit(0)
                if len(hqs) != 1:
                    print("### ERROR high quality snps not available or too many")
                    sys.exit(0)
                sample_reference=sample_reference[0]
                hqs=hqs[0]
                
                print ("--")
                print("sample name: %s" % sample_name)
                print("sample reference: %s" % sample_reference)
                print("Read 1: %s" % R1)
                print("Read 2: %s\n" % R2)
                print("directory: %s" % directory)
                print ("--")

                loc_sam=directory + "/" + sample_name
                
                os.system("samtools faidx {}" .format(sample_reference))
                os.system("picard CreateSequenceDictionary REFERENCE={} OUTPUT={}" .format(sample_reference, directory + "/" + ref + ".dict"))
                os.system("bwa index {}" .format(sample_reference))
                samfile = loc_sam + ".sam"
                allbam = loc_sam + "-all.bam"
                unmapsam = loc_sam + "-unmapped.sam"
                unmapped_read1 = loc_sam + "-unmapped_R1.fastq"
                unmapped_read2 = loc_sam + "-unmapped_R2.fastq"
                unmapped_read1gz = loc_sam + "-unmapped_R1.fastq.gz"
                unmapped_read2gz = loc_sam + "-unmapped_R2.fastq.gz"
                abyss_out = loc_sam + "-unmapped_contigs.fasta"
                sortedbam = loc_sam + "-sorted.bam"
                nodupbam = loc_sam + "-nodup.bam"
                metrics = loc_sam + "-metrics.txt"
                indel_realigner = loc_sam + ".intervals"
                realignedbam = loc_sam + "-realigned.bam"
                recal_group = loc_sam + "-recal_group"
                prebam=loc_sam + "-pre.bam"
                qualitybam = loc_sam + "-quality.bam"
                coverage_file=loc_sam + "-coverage.txt"
                hapall = loc_sam + "-hapall.vcf"
                bamout = loc_sam + "-bamout.bam"
                
                print("\n@@@ BWA mem")
                os.system("bwa mem -M -t 16 {} {} {} > {}" .format(sample_reference, R1, R2, samfile))

                print("\nAdd read group and out all BAM")
                os.system("picard AddOrReplaceReadGroups INPUT={} OUTPUT={} RGLB=lib1 RGPU=unit1 RGSM={} RGPL=illumina" .format(samfile, allbam, sample_name))
                os.system("samtools index {}" .format(allbam))

                print("\n@@@ Samtools unmapped")
                os.system("samtools view -h -f4 -T {} {} -o {}" .format(sample_reference, allbam, unmapsam))

                print("\n@@@ Unmapped to FASTQ")
                os.system("picard SamToFastq INPUT={} FASTQ={} SECOND_END_FASTQ={}" .format(unmapsam, unmapped_read1, unmapped_read2))
                
                print("\n@@@ Abyss")
                abyss_contig_count=0

                os.system("ABYSS --out {} --coverage 3 --kmer 64 {} {}" .format(abyss_out, unmapped_read1, unmapped_read2))
                try:
                    with open(abyss_out) as f:
                        for line in f:
                            abyss_contig_count += line.count(">")
                except FileNotFoundError:
                    abyss_contig_count = 0

                print("\n@@@ Sort BAM")
                os.system("samtools sort {} -o {}" .format(allbam, sortedbam))
                os.system("samtools index {}" .format(sortedbam))
                
                print("\n@@@ Write stats to file")
                stat_file = "stat_align.txt"
                stat_out = open(stat_file, 'w')
                #os.system("samtools idxstats {} > {}" .format(sortedbam, stat_out)) Doesn't work when needing to std out.
                stat_out.write(os.popen("samtools idxstats {} " .format(sortedbam)).read())
                stat_out.close()

                with open(stat_file) as f:
                    first_line = f.readline()
                    first_line = first_line.rstrip()
                    first_line=re.split(':|\t', first_line)
                    reference_sequence_name = str(first_line[0])
                    sequence_length = "{:,}".format(int(first_line[1]))
                    allbam_mapped_reads = int(first_line[2])
                    allbam_unmapped_reads = "{:,}".format(int(first_line[3]))

                print("\n@@@ Find duplicate reads")
                os.system("picard MarkDuplicates INPUT={} OUTPUT={} METRICS_FILE={} ASSUME_SORTED=true REMOVE_DUPLICATES=true" .format(sortedbam, nodupbam, metrics))
                os.system("samtools index {}" .format(nodupbam))
                
                duplicate_stat_file = "duplicate_stat_align.txt"
                duplicate_stat_out = open(duplicate_stat_file, 'w')
                #os.system("samtools idxstats {} > {}" .format(sortedbam, stat_out)) Doesn't work when needing to std out.
                duplicate_stat_out.write(os.popen("samtools idxstats {} " .format(nodupbam)).read())
                duplicate_stat_out.close()
                with open(duplicate_stat_file) as f:
                    dup_first_line = f.readline()
                    dup_first_line = dup_first_line.rstrip()
                    dup_first_line=re.split(':|\t', dup_first_line)
                    nodupbam_mapped_reads = int(dup_first_line[2])
                    nodupbam_unmapped_reads = int(dup_first_line[3])
                try:
                    unmapped_reads = allbam_mapped_reads - nodupbam_mapped_reads
                except:
                    unmapped_reads = "none_found"
                
                allbam_mapped_reads = "{:,}".format(allbam_mapped_reads)
                print(unmapped_reads)

                print("\n@@@  Realign indels")
                os.system("gatk -T RealignerTargetCreator -I {} -R {} -o {}" .format(nodupbam, sample_reference, indel_realigner))
                if not os.path.isfile(indel_realigner):
                    os.system("gatk -T RealignerTargetCreator --fix_misencoded_quality_scores -I {} -R {} -o {}" .format(nodupbam, sample_reference, indel_realigner))
                os.system("gatk -T IndelRealigner -I {} -R {} -targetIntervals {} -o {}" .format(nodupbam, sample_reference, indel_realigner, realignedbam))
                if not os.path.isfile(realignedbam):
                    os.system("gatk -T IndelRealigner --fix_misencoded_quality_scores -I {} -R {} -targetIntervals {} -o {}" .format(nodupbam, sample_reference, indel_realigner, realignedbam))

                print("\n@@@ Base recalibration")
                os.system("gatk -T BaseRecalibrator -I {} -R {} -knownSites {} -o {}". format(realignedbam, sample_reference, hqs, recal_group))
                if not os.path.isfile(realignedbam):
                    os.system("gatk -T BaseRecalibrator  --fix_misencoded_quality_scores -I {} -R {} -knownSites {} -o {}". format(realignedbam, sample_reference, hqs, recal_group))

                print("\n@@@ Make realigned BAM")
                os.system("gatk -T PrintReads -R {} -I {} -BQSR {} -o {}" .format (sample_reference, realignedbam, recal_group, prebam))
                if not os.path.isfile(prebam):
                    os.system("gatk -T PrintReads  --fix_misencoded_quality_scores -R {} -I {} -BQSR {} -o {}" .format (sample_reference, realignedbam, recal_group, prebam))

                print("\n@@@ Clip reads")
                os.system("gatk -T ClipReads -R {} -I {} -o {} -filterNoBases -dcov 10" .format(sample_reference, prebam, qualitybam))
                os.system("samtools index {}" .format(qualitybam))

                print("\n@@@ Depth of coverage using GATK")
                os.system("gatk -T DepthOfCoverage -R {} -I {} -o {} -omitIntervals --omitLocusTable --omitPerSampleStats -nt 8" .format(sample_reference, prebam, coverage_file))

                print("\n@@@ Calling SNPs with HaplotypeCaller")
                os.system("gatk -R {} -T HaplotypeCaller -I {} -o {} -bamout {} -dontUseSoftClippedBases -allowNonUniqueKmersInRef" .format(sample_reference, qualitybam, hapall, bamout))

                print("Getting Zero Coverage...\n")
                zero_coverage_vcf, good_snp_count, ave_coverage, genome_coverage = script1.add_zero_coverage(coverage_file, hapall, loc_sam)

                ###
                if gbk_file is not "None":
                    try:
                        in_annotation_as_dict = SeqIO.to_dict(SeqIO.parse(gbk_file, "genbank"))
                        annotated_vcf = loc_sam + "-annotated.vcf"
                        write_out=open(annotated_vcf, 'w')
                        
                        with open(zero_coverage_vcf) as vfile:
                            print("finding annotations...\n")
                            for line in vfile:
                                annotated_line = script1.get_annotations(line, in_annotation_as_dict)
                                print("%s" % annotated_line, file=write_out)
                        write_out.close()
                    except AttributeError:
                        pass
    #
    #            with open(zero_coverage_vcf) as vfile:
    #                print("finding annotations...\n")
    #                with futures.ProcessPoolExecutor() as pool:
    #                    for annotated_line in pool.map(partial(script1.get_annotations, in_annotation_as_dict = in_annotation_as_dict), vfile): #function, passed arguement, list
    #                        print("%s" % annotated_line, file=write_out)
    #            write_out.close()
                ###

                os.remove(samfile)
                os.remove(allbam)
                os.remove(nodupbam)
                os.remove(nodupbam + ".bai")
                os.remove(unmapsam)
                os.remove(sortedbam)
                os.remove(sortedbam + ".bai")
                os.remove(indel_realigner)
                os.remove(realignedbam)
                os.remove(loc_sam + "-realigned.bai")
                os.remove(recal_group)
                os.remove(prebam)
                os.remove(loc_sam + "-pre.bai")
                os.remove(hqs)
                os.remove(hqs + ".idx")
                os.remove(sample_reference + ".amb")
                os.remove(sample_reference + ".ann")
                os.remove(sample_reference + ".bwt")
                os.remove(sample_reference + ".pac")
                os.remove(sample_reference + ".sa")
                os.remove(ref + ".dict")
                os.remove(duplicate_stat_file)
                os.remove(stat_file)

                unmapped = directory + "/unmapped"
                os.makedirs(unmapped)

                newZip = zipfile.ZipFile(unmapped_read1gz, 'w')
                newZip.write(unmapped_read1, compress_type=zipfile.ZIP_DEFLATED)
                newZip.close()
                newZip = zipfile.ZipFile(unmapped_read2gz, 'w')
                newZip.write(unmapped_read2, compress_type=zipfile.ZIP_DEFLATED)
                newZip.close()
                os.remove(unmapped_read1)
                os.remove(unmapped_read2)
                
                try:
                    shutil.move(unmapped_read1gz, unmapped)
                    shutil.move(unmapped_read2gz, unmapped)
                    shutil.move(abyss_out, unmapped)
                except FileNotFoundError:
                    pass
                
                alignment = directory + "/alignment"
                os.makedirs(alignment)
                movefiles = glob.glob('*-*')
                for i in movefiles:
                    shutil.move(i, alignment)
                try:
                    shutil.move(sample_reference, alignment)
                    shutil.move(sample_reference + ".fai", alignment)
                except shutil.Error:
                    pass
                except FileNotFoundError:
                    pass
                except FileExistsError:
                    pass

                runtime = (datetime.now() - startTime)
                print ("\n\nruntime: %s:  \n" % runtime)
                ave_coverage = "{:0.1f}".format(float(ave_coverage))
                print("average_coverage: %s" % ave_coverage)

                R1size = script1.sizeof_fmt(os.path.getsize(R1))
                R2size = script1.sizeof_fmt(os.path.getsize(R2))

                try:
                    with open("mlst.txt") as f:
                        first_line = f.readline()
                        mlst_type = first_line.rstrip()
                        first_line = first_line.split()
                        mlst_type = first_line[1:]
                        mlst_type = '-'.join(mlst_type)
                except FileNotFoundError:
                    mlst_type = "N/A"

                try:
                    with open("spoligo.txt") as f:
                        first_line = f.readline()
                        first_line = first_line.rstrip()
                        first_line = first_line.split()
                        octalcode = first_line[0]
                        sbcode = first_line[1]
                        hexcode = first_line[2]
                        binarycode = first_line[3]
                except FileNotFoundError:
                    octalcode = "N/A"
                    sbcode = "N/A"
                    hexcode = "N/A"
                    binarycode = "N/A"

                sequence_count = 0
                total_length = 0
                with gzip.open(R2, "rt") as handle:
                    for r in SeqIO.parse(handle, "fastq"):
                        total_length = total_length + len(r.seq)
                        sequence_count = sequence_count + 1
                ave_read_length = total_length/sequence_count
                ave_read_length = "{:0.1f}".format(float(ave_read_length))

                stat_summary={}
                stat_summary["01-sample_name"] = sample_name
                stat_summary["02-self.species"] = self.species
                stat_summary["03-reference_sequence_name"] = reference_sequence_name
                stat_summary["04-R1size"] = R1size
                stat_summary["05-R2size"] = R2size
                stat_summary["06-allbam_mapped_reads"] = allbam_mapped_reads
                stat_summary["07-genome_coverage"] = genome_coverage
                stat_summary["08-ave_coverage"] = ave_coverage
                stat_summary["09-ave_read_length"] = ave_read_length
                stat_summary["10-unmapped_reads"] = unmapped_reads
                stat_summary["11-abyss_contig_count"] = abyss_contig_count
                stat_summary["12-good_snp_count"] = good_snp_count
                stat_summary["13-mlst_type"] = mlst_type
                stat_summary["14-octalcode"] = octalcode
                stat_summary["15-sbcode"] = sbcode
                stat_summary["16-hexcode"] = hexcode
                stat_summary["17-binarycode"] = binarycode

                stat_summary=OrderedDict(sorted(stat_summary.items()))

                for k, v in stat_summary.items():
                    print("%s: %s" % (k, v))
                
                ###
                # Create a sample stats file in the sample's script1 directory
                ts = time.time()
                st = datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')
                summary_file = loc_sam + "_" + st + '.xlsx'
                workbook = xlsxwriter.Workbook(summary_file)
                worksheet = workbook.add_worksheet()
                row = 0
                col = 0

                top_row_header = ["sample_name", "self.species", "reference_sequence_name", "R1size", "R2size", "allbam_mapped_reads", "genome_coverage", "ave_coverage", "ave_read_length", "unmapped_reads", "unmapped_assembled_contigs", "good_snp_count", "mlst_type", "octalcode", "sbcode", "hexadecimal_code", "binarycode"]
                for header in top_row_header:
                    worksheet.write(row, col, header)
                    col += 1
                col = 0
                row += 1
                for v in stat_summary.values():
                        worksheet.write(row, col, v)
                        col += 1
                workbook.close()
                ###
                
                
                return(stat_summary)



###############################################
###############################################
##################script2######################
###############################################
###############################################

class script2():

    def run_script2(self):

        home = os.path.expanduser("~")

        #os.environ["DISPLAY"]=":99"
        #xvfb = subprocess.Popen(['Xvfb', ':99']) # allows not needing to use -X flag when ssh'ing into session.
        #Manage headless displays with Xvfb (X virtual framebuffer

        if xvfb_available:
            try:
                vdisplay = Xvfb()
                vdisplay.start()
                vdisplay_status=True
            except RuntimeError:
                print("##### Xvfb did not start")
                print("##### PDFs and SVGs will not be made")
                vdisplay_status=False
                time.sleep(3) # pause to see files will not be made
            except OSError:
                print("##### Xvfb did not start")
                print("##### PDFs and SVGs will not be made")
                vdisplay_status=False
                time.sleep(3) # pause to see files will not be made

        error_list = []

        try:
            subprocess.call("raxml")
            sys_raxml = "raxml"
            print ("%s found" % sys_raxml)
        except OSError:
            print ("looking for RAxML")
            try:
                subprocess.call("raxmlHPC-SSE3")
                sys_raxml = "raxmlHPC-SSE3"
                print ("%s found" % sys_raxml)
            except OSError:
                print ("looking for RAxML")
                try:
                    subprocess.call("raxmlHPC-PTHREADS-AVX2")
                    sys_raxml = "raxmlHPC-PTHREADS-AVX2"
                    print ("RAxML found")
                except OSError:
                    print ("#####RAxML is not in you PATH")
                    print ("#####See help page for support")
                    sys.exit(0)

        print ("\n\nRAxML found in $PATH as: %s" % sys_raxml)

        #set cpu usage
        cpu_count = multiprocessing.cpu_count()

        if cpu_count < 20:
            raxml_cpu = 2
        else:
            raxml_cpu = int(cpu_count/10)
        
        def update_directory(dependents_dir): # UPDATE DIRECTORIES
            home = os.path.expanduser("~")
            
            if os.path.isdir("/bioinfo11/TStuber/Results"): #check bioinfo from server
                upload_to = "/bioinfo11/TStuber/Results"
                remote="/bioinfo11/TStuber/Results" + dependents_dir
                if os.path.isdir("/Users/Shared"):
                    dep_path = "/Users/Shared"
                    dir_split = dependents_dir.split('/')[1:]
                    for i in dir_split:
                        dep_path += '/' + i
                        if not os.path.exists(dep_path):
                            os.makedirs(dep_path)
                    local = "/Users/Shared" + dependents_dir
                    if os.path.isdir(local):
                        try:
                            shutil.rmtree(local)
                            shutil.copytree(remote, local)
                        except:
                            pass
                elif os.path.isdir("/home/shared"):
                    dep_path = "/home/shared"
                    dir_split = dependents_dir.split('/')[1:]
                    for i in dir_split:
                        dep_path += '/' + i
                        if not os.path.exists(dep_path):
                            os.makedirs(dep_path)
                    local = "/home/shared" + dependents_dir
                    if os.path.isdir(local):
                        try:
                            shutil.rmtree(local)
                            shutil.copytree(remote, local)
                        except:
                            pass

            elif os.path.isdir("/Volumes/root/TStuber/Results"): #check bioinfo from Mac
                upload_to = "/Volumes/root/TStuber/Results"
                remote="/Volumes/root/TStuber/Results" + dependents_dir
                if os.path.isdir("/Users/Shared"):
                    dep_path = "/Users/Shared"
                    dir_split = dependents_dir.split('/')[1:]
                    for i in dir_split:
                        dep_path += '/' + i
                        if not os.path.exists(dep_path):
                            os.makedirs(dep_path)
                    local = "/Users/Shared" + dependents_dir
                    if os.path.isdir(local):
                        try:
                            shutil.rmtree(local)
                            shutil.copytree(remote, local)
                        except:
                            pass
                elif os.path.isdir("/home/shared"):
                    dep_path = "/home/shared"
                    dir_split = dependents_dir.split('/')[1:]
                    for i in dir_split:
                        dep_path += '/' + i
                        if not os.path.exists(dep_path):
                            os.makedirs(dep_path)
                    local = "/home/shared" + dependents_dir
                    if os.path.isdir(local):
                        try:
                            shutil.rmtree(local)
                            shutil.copytree(remote, local)
                        except:
                            pass

            #### PLACE A CHECK FROM GITHUB
            
            elif os.path.isdir("/Users/Shared" + dependents_dir): #check local copy in shared folder
                upload_to ="not_found"
                remote = "not_found"
                local = "/Users/Shared" + dependents_dir
                    
            elif os.path.isdir("/home/shared" + dependents_dir): #check local copy in shared folder
                upload_to ="not_found"
                remote = "not_found"
                local = "/home/shared" + dependents_dir
            
            elif os.path.isdir(home + "/dependencies" + dependents_dir): #check local copy from Git repo
                upload_to ="not_found"
                remote = "no remote"
                script_location = home # points to home directory
                local = home + "/dependencies" + dependents_dir # sets dependencies directory to home directory
            else:
                os.makedirs(home + "/dependencies")
                print("\n\nDOWNLOADING DEPENDENCIES FROM GITHUB... ***\n\n")
                git.Repo.clone_from("https://github.com/stuber/dependencies.git", home + "/dependencies")
                upload_to ="not_found"
                remote = "no remote"
                script_location = home # points to home directory
                local = home + "/dependencies" + dependents_dir # sets dependencies directory to home directory
            
            print("\n####################DIRECTORY LOCATION")
            print("####################upload_to: %s" % upload_to)
            print("####################remote: %s" % remote)
            print("####################local: %s\n" % local)
            
            return upload_to, remote, local
        
        # Get filters set up
        def get_filters(excelinfile, filter_files):
            for i in glob.glob(filter_files + "/*"):
                os.remove(i)

            wb = xlrd.open_workbook(excelinfile)
            sheets = wb.sheet_names()
            for sheet in sheets:
                ws = wb.sheet_by_name(sheet)

                myrange = lambda start, end: range(start, end+1)

                for colnum in range(ws.ncols): # for each column in worksheet
                    file_out = filter_files + "/" + ws.col_values(colnum)[0] + ".txt" # column header naming file
                    write_out = open (file_out, 'at')
                    mylist = ws.col_values(colnum)[1:] # list of each field in column, minus the header
                    mylist = [x for x in mylist if x] # remove blank cells
                    for value in mylist:
                        value = str(value)
                        value = value.replace(sheet + "-", '')
                        if "-" not in value:
                            value=int(float(value)) # change str to float to int
                            print (sheet + "-" + str(value), file=write_out)
                        elif "-" in value:
                            value = value.split("-")
                            for i in range(int(value[0]), int(value[1]) + 1 ):
                                print (sheet + "-" + str(i), file=write_out)
            write_out.close()
            
### SET PARAMETERS
        global qual_gatk_threshold
        global N_gatk_threshold
        global bruc_private_codes
        global genotypingcodes
        global gbk_file
        global definingSNPs
        global remove_from_analysis
        global excelinfile
        global bioinfoVCF
        global filter_files
        global email_list

        if options.species == "suis1":

            qual_gatk_threshold = 300
            N_gatk_threshold = 350
            
            #Remove network path at and left of "Results"
            dependents_dir="/brucella/suis1/script_dependents/script2"
            
            upload_to, remote, script_dependents = update_directory(dependents_dir) # returned upload_to, remote, local (aka: script_dependents) --> local is where working dependencies are located
            
            bruc_private_codes(upload_to) # if f drive then upload fixed column 32 to bioinfo
            try:
                shutil.copy(upload_to + "/brucella/genotyping_codes.xlsx", script_dependents)
            except FileNotFoundError:
                print ("will use previously used genotyping_codes.xlsx file")

            genotypingcodes = script_dependents + "/genotyping_codes.xlsx" # this may not be available if there is no access to f drive.  f drive record will not get cp to cut bioinfo list and then cp locally.  Can also manually put something in ~/dependencies on github.
            gbk_file = script_dependents + "/NC_017251-NC_017250.gbk"
            # This file tells the script how to cluster VCFs
            definingSNPs = script_dependents + "/DefiningSNPsGroupDesignations_python.xlsx"
            remove_from_analysis = script_dependents + "/RemoveFromAnalysis.xlsx"
            bioinfoVCF = upload_to + "/brucella/suis1/vcfs"
            excelinfile = script_dependents + "/Filtered_Regions_python.xlsx"
            print(excelinfile)
            filter_files = script_dependents + "/filter_files"
            if os.path.isdir(filter_files):
                shutil.rmtree(filter_files)
                os.mkdir(filter_files)
            else:        os.mkdir(filter_files)
            get_filters(excelinfile, filter_files) #***FUNCTION CALL
            if options.email == "s":
                email_list = "tod.p.stuber@aphis.usda.gov, jessica.a.hicks@aphis.usda.gov, christine.r.quance@aphis.usda.gov, suelee.robbe-austerman@aphis.usda.gov"

        elif options.species == "suis3":

            qual_gatk_threshold = 300
            N_gatk_threshold = 350
            
            #Remove network path at and left of "Results"
            dependents_dir="/brucella/suis3/script_dependents/script2"
            
            upload_to, remote, script_dependents = update_directory(dependents_dir) # returned upload_to, remote, local  --> local is where working dependencies are located
            bruc_private_codes(upload_to)
            try:
                shutil.copy(upload_to + "/brucella/genotyping_codes.xlsx", script_dependents)
            except FileNotFoundError:
                print ("will use previously used genotyping_codes.xlsx file")

            genotypingcodes = script_dependents + "/genotyping_codes.xlsx"
            gbk_file = script_dependents + "/NZ_CP007719-NZ_CP007718.gbk"
            # This file tells the script how to cluster VCFs
            definingSNPs = script_dependents + "/DefiningSNPsGroupDesignations_python.xlsx"
            remove_from_analysis = script_dependents + "/RemoveFromAnalysis.xlsx"
            bioinfoVCF = upload_to + "/brucella/suis3/vcfs"
            excelinfile = script_dependents + "/Filtered_Regions_python.xlsx"
            print(excelinfile)
            filter_files = script_dependents + "/filter_files"
            if os.path.isdir(filter_files):
                shutil.rmtree(filter_files)
                os.mkdir(filter_files)
            else:        os.mkdir(filter_files)
            get_filters(excelinfile, filter_files) #***FUNCTION CALL
            if options.email == "s":
                email_list = "tod.p.stuber@aphis.usda.gov, jessica.a.hicks@aphis.usda.gov, christine.r.quance@aphis.usda.gov, suelee.robbe-austerman@aphis.usda.gov"

        elif options.species == "suis4":

            qual_gatk_threshold = 300
            N_gatk_threshold = 350
            
            #Remove network path at and left of "Results"
            dependents_dir="/brucella/suis4/script_dependents/script2"
            
            upload_to, remote, script_dependents = update_directory(dependents_dir) #***FUNCTION CALL
            bruc_private_codes(upload_to)
            try:
                shutil.copy(upload_to + "/brucella/genotyping_codes.xlsx", script_dependents)
            except FileNotFoundError:
                print ("will use previously used genotyping_codes.xlsx file")

            genotypingcodes = script_dependents + "/genotyping_codes.xlsx"
            #gbk_file = script_dependents + ""
            # This file tells the script how to cluster VCFs
            definingSNPs = script_dependents + "/DefiningSNPsGroupDesignations_python.xlsx"
            remove_from_analysis = script_dependents + "/RemoveFromAnalysis.xlsx"
            bioinfoVCF = upload_to + "/brucella/suis4/vcfs"
            excelinfile = script_dependents + "/Filtered_Regions_python.xlsx"
            print(excelinfile)
            filter_files = script_dependents + "/filter_files"
            if os.path.isdir(filter_files):
                shutil.rmtree(filter_files)
                os.mkdir(filter_files)
            else:        os.mkdir(filter_files)
            get_filters(excelinfile, filter_files) #***FUNCTION CALL
            if options.email == "s":
                email_list = "tod.p.stuber@aphis.usda.gov, jessica.a.hicks@aphis.usda.gov, christine.r.quance@aphis.usda.gov, suelee.robbe-austerman@aphis.usda.gov"

        elif options.species == "ab1":

            qual_gatk_threshold = 300
            N_gatk_threshold = 350
            
            #Remove network path at and left of "Results"
            dependents_dir="/brucella/abortus1/script_dependents/script2"
            
            upload_to, remote, script_dependents = update_directory(dependents_dir) #***FUNCTION CALL
            bruc_private_codes(upload_to)
            try:
                shutil.copy(upload_to + "/brucella/genotyping_codes.xlsx", script_dependents)
            except FileNotFoundError:
                print ("will use previously used genotyping_codes.xlsx file")

            genotypingcodes = script_dependents + "/genotyping_codes.xlsx"
            gbk_file = script_dependents + "/NC_006932-NC_006933.gbk"
            # This file tells the script how to cluster VCFs
            definingSNPs = script_dependents + "/DefiningSNPsGroupDesignations_python.xlsx"
            remove_from_analysis = script_dependents + "/RemoveFromAnalysis.xlsx"
            bioinfoVCF = upload_to + "/brucella/abortus1/vcfs"
            excelinfile = script_dependents + "/Filtered_Regions_python.xlsx"
            print(excelinfile)
            filter_files = script_dependents + "/filter_files"
            if os.path.isdir(filter_files):
                shutil.rmtree(filter_files)
                os.mkdir(filter_files)
            else:        os.mkdir(filter_files)
            get_filters(excelinfile, filter_files) #***FUNCTION CALL
            if options.email == "s":
                email_list = "tod.p.stuber@aphis.usda.gov, jessica.a.hicks@aphis.usda.gov, christine.r.quance@aphis.usda.gov, suelee.robbe-austerman@aphis.usda.gov"

        elif options.species == "ab3":

            qual_gatk_threshold = 300
            N_gatk_threshold = 350
            
            #Remove network path at and left of "Results"
            dependents_dir="/brucella/abortus3/script_dependents/script2"
            
            upload_to, remote, script_dependents = update_directory(dependents_dir) #***FUNCTION CALL
            bruc_private_codes(upload_to)
            try:
                shutil.copy(upload_to + "/brucella/genotyping_codes.xlsx", script_dependents)
            except FileNotFoundError:
                print ("will use previously used genotyping_codes.xlsx file")

            genotypingcodes = script_dependents + "/genotyping_codes.xlsx"
            gbk_file = script_dependents + "/CP007682-CP007683.gbk"
            # This file tells the script how to cluster VCFs
            definingSNPs = script_dependents + "/DefiningSNPsGroupDesignations_python.xlsx"
            remove_from_analysis = script_dependents + "/RemoveFromAnalysis.xlsx"
            bioinfoVCF = upload_to + "/brucella/abortus3/vcfs"
            excelinfile = script_dependents + "/Filtered_Regions_python.xlsx"
            print(excelinfile)
            filter_files = script_dependents + "/filter_files"
            if os.path.isdir(filter_files):
                shutil.rmtree(filter_files)
                os.mkdir(filter_files)
            else:        os.mkdir(filter_files)
            get_filters(excelinfile, filter_files) #***FUNCTION CALL
            if options.email == "s":
                email_list = "tod.p.stuber@aphis.usda.gov, jessica.a.hicks@aphis.usda.gov, christine.r.quance@aphis.usda.gov, suelee.robbe-austerman@aphis.usda.gov"

        elif options.species == "mel1":

            qual_gatk_threshold = 300
            N_gatk_threshold = 350
            
            #Remove network path at and left of "Results"
            dependents_dir="/brucella/melitensis-bv1/script_dependents/script2"
            
            upload_to, remote, script_dependents = update_directory(dependents_dir) #***FUNCTION CALL
            bruc_private_codes(upload_to)
            try:
                shutil.copy(upload_to + "/brucella/genotyping_codes.xlsx", script_dependents)
            except FileNotFoundError:
                print ("will use previously used genotyping_codes.xlsx file")

            genotypingcodes = script_dependents + "/genotyping_codes.xlsx"
            gbk_file = script_dependents + "/NC_003317-NC_003318.gbk"
            # This file tells the script how to cluster VCFs
            definingSNPs = script_dependents + "/DefiningSNPsGroupDesignations_python.xlsx"
            remove_from_analysis = script_dependents + "/RemoveFromAnalysis.xlsx"
            bioinfoVCF = upload_to + "/brucella/melitensis-bv1/vcfs"
            excelinfile = script_dependents + "/Filtered_Regions_python.xlsx"
            print(excelinfile)
            filter_files = script_dependents + "/filter_files"
            if os.path.isdir(filter_files):
                shutil.rmtree(filter_files)
                os.mkdir(filter_files)
            else:        os.mkdir(filter_files)
            get_filters(excelinfile, filter_files) #***FUNCTION CALL
            if options.email == "s":
                email_list = "tod.p.stuber@aphis.usda.gov, jessica.a.hicks@aphis.usda.gov, christine.r.quance@aphis.usda.gov, suelee.robbe-austerman@aphis.usda.gov"

        elif options.species == "mel2":

            qual_gatk_threshold = 300
            N_gatk_threshold = 350
            
            #Remove network path at and left of "Results"
            dependents_dir="/brucella/melitensis-bv2/script_dependents/script2"
            
            upload_to, remote, script_dependents = update_directory(dependents_dir) #***FUNCTION CALL
            bruc_private_codes(upload_to)
            try:
                shutil.copy(upload_to + "/brucella/genotyping_codes.xlsx", script_dependents)
            except FileNotFoundError:
                print ("will use previously used genotyping_codes.xlsx file")

            genotypingcodes = script_dependents + "/genotyping_codes.xlsx"
            gbk_file = script_dependents + "/NC_012441-NC_012442.gbk"
            # This file tells the script how to cluster VCFs
            definingSNPs = script_dependents + "/DefiningSNPsGroupDesignations_python.xlsx"
            remove_from_analysis = script_dependents + "/RemoveFromAnalysis.xlsx"
            bioinfoVCF = upload_to + "/brucella/melitensis-bv2/vcfs"
            excelinfile = script_dependents + "/Filtered_Regions_python.xlsx"
            print(excelinfile)
            filter_files = script_dependents + "/filter_files"
            if os.path.isdir(filter_files):
                shutil.rmtree(filter_files)
                os.mkdir(filter_files)
            else:        os.mkdir(filter_files)
            get_filters(excelinfile, filter_files) #***FUNCTION CALL
            if options.email == "s":
                email_list = "tod.p.stuber@aphis.usda.gov, jessica.a.hicks@aphis.usda.gov, christine.r.quance@aphis.usda.gov, suelee.robbe-austerman@aphis.usda.gov"

        elif options.species == "mel3":

            qual_gatk_threshold = 300
            N_gatk_threshold = 350
            
            #Remove network path at and left of "Results"
            dependents_dir="/brucella/melitensis-bv3/script_dependents/script2"
            
            upload_to, remote, script_dependents = update_directory(dependents_dir) #***FUNCTION CALL
            bruc_private_codes(upload_to)
            try:
                shutil.copy(upload_to + "/brucella/genotyping_codes.xlsx", script_dependents)
            except FileNotFoundError:
                print ("will use previously used genotyping_codes.xlsx file")

            genotypingcodes = script_dependents + "/genotyping_codes.xlsx"
            gbk_file = script_dependents + "/NZ_CP007760-NZ_CP007761.gbk"
            # This file tells the script how to cluster VCFs
            definingSNPs = script_dependents + "/DefiningSNPsGroupDesignations_python.xlsx"
            remove_from_analysis = script_dependents + "/RemoveFromAnalysis.xlsx"
            bioinfoVCF = upload_to + "/brucella/melitensis-bv3/vcfs"
            excelinfile = script_dependents + "/Filtered_Regions_python.xlsx"
            print(excelinfile)
            filter_files = script_dependents + "/filter_files"
            if os.path.isdir(filter_files):
                shutil.rmtree(filter_files)
                os.mkdir(filter_files)
            else:        os.mkdir(filter_files)
            get_filters(excelinfile, filter_files) #***FUNCTION CALL
            if options.email == "s":
                email_list = "tod.p.stuber@aphis.usda.gov, jessica.a.hicks@aphis.usda.gov, christine.r.quance@aphis.usda.gov, suelee.robbe-austerman@aphis.usda.gov"

        elif options.species == "canis":

            qual_gatk_threshold = 300
            N_gatk_threshold = 350
            
            #Remove network path at and left of "Results"
            dependents_dir="/brucella/canis/script_dependents/script2"
            
            upload_to, remote, script_dependents = update_directory(dependents_dir) #***FUNCTION CALL
            bruc_private_codes(upload_to)
            try:
                shutil.copy(upload_to + "/brucella/genotyping_codes.xlsx", script_dependents)
            except FileNotFoundError:
                print ("will use previously used genotyping_codes.xlsx file")

            genotypingcodes = script_dependents + "/genotyping_codes.xlsx"
            gbk_file = script_dependents + "/NC_010103-NC_010104.gbk"
            # This file tells the script how to cluster VCFs
            definingSNPs = script_dependents + "/DefiningSNPsGroupDesignations_python.xlsx"
            remove_from_analysis = script_dependents + "/RemoveFromAnalysis.xlsx"
            bioinfoVCF = upload_to + "/brucella/canis/vcfs"
            excelinfile = script_dependents + "/Filtered_Regions_python.xlsx"
            print(excelinfile)
            filter_files = script_dependents + "/filter_files"
            if os.path.isdir(filter_files):
                shutil.rmtree(filter_files)
                os.mkdir(filter_files)
            else:        os.mkdir(filter_files)
            get_filters(excelinfile, filter_files) #***FUNCTION CALL
            if options.email == "s":
                email_list = "tod.p.stuber@aphis.usda.gov, jessica.a.hicks@aphis.usda.gov, christine.r.quance@aphis.usda.gov, suelee.robbe-austerman@aphis.usda.gov"

        elif options.species == "ceti1":

            qual_gatk_threshold = 300
            N_gatk_threshold = 350
            
            #Remove network path at and left of "Results"
            dependents_dir="/brucella/ceti1/script_dependents/script2"
            
            upload_to, remote, script_dependents = update_directory(dependents_dir) #***FUNCTION CALL
            bruc_private_codes(upload_to)
            try:
                shutil.copy(upload_to + "/brucella/genotyping_codes.xlsx", script_dependents)
            except FileNotFoundError:
                print ("will use previously used genotyping_codes.xlsx file")

            genotypingcodes = script_dependents + "/genotyping_codes.xlsx"
            #gbk_file = script_dependents + ""
            # This file tells the script how to cluster VCFs
            definingSNPs = script_dependents + "/DefiningSNPsGroupDesignations_python.xlsx"
            remove_from_analysis = script_dependents + "/RemoveFromAnalysis.xlsx"
            bioinfoVCF = upload_to + "/brucella/ceti1/vcfs"
            excelinfile = script_dependents + "/Filtered_Regions.xlsx"
            print(excelinfile)
            filter_files = script_dependents + "/filter_files"
            if os.path.isdir(filter_files):
                shutil.rmtree(filter_files)
                os.mkdir(filter_files)
            else:        os.mkdir(filter_files)
            get_filters(excelinfile, filter_files) #***FUNCTION CALL
            if options.email == "s":
                email_list = "tod.p.stuber@aphis.usda.gov, jessica.a.hicks@aphis.usda.gov, christine.r.quance@aphis.usda.gov, suelee.robbe-austerman@aphis.usda.gov"

        elif options.species == "ceti2":

            qual_gatk_threshold = 300
            N_gatk_threshold = 350
            
            #Remove network path at and left of "Results"
            dependents_dir="/brucella/ceti2/script_dependents/script2"
            
            upload_to, remote, script_dependents = update_directory(dependents_dir) #***FUNCTION CALL
            bruc_private_codes(upload_to)
            try:
                shutil.copy(upload_to + "/brucella/genotyping_codes.xlsx", script_dependents)
            except FileNotFoundError:
                print ("will use previously used genotyping_codes.xlsx file")

            genotypingcodes = script_dependents + "/genotyping_codes.xlsx"
            gbk_file = script_dependents + "/NC_022905-NC_022906.gbk"
            # This file tells the script how to cluster VCFs
            definingSNPs = script_dependents + "/DefiningSNPsGroupDesignations_python.xlsx"
            remove_from_analysis = script_dependents + "/RemoveFromAnalysis.xlsx"
            bioinfoVCF = upload_to + "/brucella/ceti2/vcfs"
            excelinfile = script_dependents + "/Filtered_Regions.xlsx"
            print(excelinfile)
            filter_files = script_dependents + "/filter_files"
            if os.path.isdir(filter_files):
                shutil.rmtree(filter_files)
                os.mkdir(filter_files)
            else:        os.mkdir(filter_files)
            get_filters(excelinfile, filter_files) #***FUNCTION CALL
            if options.email == "s":
                email_list = "tod.p.stuber@aphis.usda.gov, jessica.a.hicks@aphis.usda.gov, christine.r.quance@aphis.usda.gov, suelee.robbe-austerman@aphis.usda.gov"

        elif options.species == "bovis":
            
            qual_gatk_threshold = 150
            N_gatk_threshold = 200
            
            #Remove network path at and left of "Results"
            dependents_dir="/mycobacterium/tbc/tbbov/script_dependents/script2"
            
            upload_to, remote, script_dependents = update_directory(dependents_dir) #***FUNCTION CALL
            try:
                shutil.copy(upload_to + "/mycobacterium/genotyping_codes.xlsx", script_dependents)
            except FileNotFoundError:
                print ("will use previously used genotyping_codes.xlsx file")
            genotypingcodes = script_dependents + "/genotyping_codes.xlsx"
            gbk_file = script_dependents + "/NC_002945.gbk"
            # This file tells the script how to cluster VCFs
            definingSNPs = script_dependents + "/DefiningSNPsGroupDesignations_python.xlsx"
            remove_from_analysis = script_dependents + "/RemoveFromAnalysis.xlsx"
            bioinfoVCF = upload_to + "/mycobacterium/tbc/tbbov/script2"
            excelinfile = script_dependents + "/Filtered_Regions_python.xlsx"
            filter_files = script_dependents + "/filter_files"
            print ("filter_files %s" % filter_files)
            if os.path.isdir(filter_files):
                shutil.rmtree(filter_files)
                os.mkdir(filter_files)
            else:
                os.mkdir(filter_files)
            get_filters(excelinfile, filter_files) #***FUNCTION CALL
            if not options.email:
                email_list = "tod.p.stuber@aphis.usda.gov, jessica.a.hicks@aphis.usda.gov, suelee.robbe-austerman@aphis.usda.gov"

        elif options.species == "af":
            
            qual_gatk_threshold = 150
            N_gatk_threshold = 200
            
            #Remove network path at and left of "Results"
            dependents_dir="/mycobacterium/tbc/af2122/script_dependents/script2"
            
            upload_to, remote, script_dependents = update_directory(dependents_dir) #***FUNCTION CALL
            try:
                shutil.copy(upload_to + "/mycobacterium/genotyping_codes.xlsx", script_dependents)
            except FileNotFoundError:
                print ("will use previously used genotyping_codes.xlsx file")
            genotypingcodes = script_dependents + "/genotyping_codes.xlsx"
            gbk_file = script_dependents + "/NC_002945v4.gbk"
            # This file tells the script how to cluster VCFs
            definingSNPs = script_dependents + "/DefiningSNPsGroupDesignations.xlsx"
            remove_from_analysis = script_dependents + "/RemoveFromAnalysis.xlsx"
            bioinfoVCF = upload_to + "/mycobacterium/tbc/af/script2"
            excelinfile = script_dependents + "/Filtered_Regions.xlsx"
            filter_files = script_dependents + "/filter_files"
            print ("filter_files %s" % filter_files)
            if os.path.isdir(filter_files):
                shutil.rmtree(filter_files)
                os.mkdir(filter_files)
            else:
                os.mkdir(filter_files)
            get_filters(excelinfile, filter_files) #***FUNCTION CALL
            if not options.email:
                email_list = "tod.p.stuber@aphis.usda.gov, jessica.a.hicks@aphis.usda.gov, suelee.robbe-austerman@aphis.usda.gov"

        elif options.species == "h37":
            
            qual_gatk_threshold = 150
            N_gatk_threshold = 200
            
            #Remove network path at and left of "Results"
            dependents_dir="/mycobacterium/tbc/h37/script_dependents/script2"
            
            upload_to, remote, script_dependents = update_directory(dependents_dir) #***FUNCTION CALL
            try:
                shutil.copy(upload_to + "/mycobacterium/genotyping_codes.xlsx", script_dependents)
            except FileNotFoundError:
                print ("will use previously used genotyping_codes.xlsx file")

            genotypingcodes = script_dependents + "/genotyping_codes.xlsx"
            gbk_file = script_dependents + "/NC_000962.gbk"
            # This file tells the script how to cluster VCFs
            definingSNPs = script_dependents + "/DefiningSNPsGroupDesignations_python.xlsx"
            remove_from_analysis = script_dependents + "/RemoveFromAnalysis.xlsx"
            bioinfoVCF = upload_to + "/mycobacterium/tbc/h37/script2"
            excelinfile = script_dependents + "/Filtered_Regions_python.xlsx"
            filter_files = script_dependents + "/filter_files"
            if os.path.isdir(filter_files):
                shutil.rmtree(filter_files)
                os.mkdir(filter_files)
            else:        os.mkdir(filter_files)
            get_filters(excelinfile, filter_files) #***FUNCTION CALL
            if options.email == "s":
                email_list = "tod.p.stuber@aphis.usda.gov, jessica.a.hicks@aphis.usda.gov, suelee.robbe-austerman@aphis.usda.gov"

        elif options.species == "para":
            
            qual_gatk_threshold = 150
            N_gatk_threshold = 200
            
            #Remove network path at and left of "Results"
            dependents_dir="/mycobacterium/avium_complex/para_cattle-bison/script_dependents/script2"
            
            upload_to, remote, script_dependents = update_directory(dependents_dir) #***FUNCTION CALL
            try:
                shutil.copy(upload_to + "/mycobacterium/avium_complex/avium_genotyping_codes.xlsx", script_dependents)
            except FileNotFoundError:
                print ("will use previously used genotyping_codes.xlsx file")

            genotypingcodes = script_dependents + "/avium_genotyping_codes.xlsx"
            gbk_file = script_dependents + "/NC_002944.gbk"
            # This file tells the script how to cluster VCFs
            definingSNPs = script_dependents + "/DefiningSNPsGroupDesignations.xlsx"
            remove_from_analysis = script_dependents + "/RemoveFromAnalysis.xlsx"
            bioinfoVCF = upload_to + "/mycobacterium/avium_complex/para_cattle-bison/vcfs"
            excelinfile = script_dependents + "/Filtered_Regions.xlsx"
            filter_files = script_dependents + "/filter_files"
            if os.path.isdir(filter_files):
                shutil.rmtree(filter_files)
                os.mkdir(filter_files)
            else:        os.mkdir(filter_files)
            get_filters(excelinfile, filter_files) #***FUNCTION CALL
            if options.email == "s":
                email_list = "tod.p.stuber@aphis.usda.gov, jessica.a.hicks@aphis.usda.gov, suelee.robbe-austerman@aphis.usda.gov"

        else:
            parser.print_help()
            print ("\n#####EXIT AT SETTING OPTIONS, Check that a \"-s\" species was provided\n")
            sys.exit(0)

        print ("\nSET VARIABLES")
        print ("\tgenotypingcodes: %s " % genotypingcodes)

        cpu_count = int(cpu_count/2.3)

        htmlfile_name = root_dir+ "/summary_log.html"
        htmlfile = open(htmlfile_name, 'at')

        startTime = datetime.now()
        print ("\n\n*** START ***\n")
        print ("Start time: %s" % startTime)

        # DIRECTORY TEST AND BACKUP
        if getattr(sys, 'frozen', False):
            script_used = os.path.realpath(sys.executable)
        elif __file__:
            script_used = os.path.realpath(__file__)

        print ("\nScript used: %s \n" % script_used)

        # make backup
        os.makedirs('starting_files')
        all_starting_files = glob.glob('*vcf')
        for i in all_starting_files:
            shutil.copy(i, 'starting_files')

        ##################
        # FUNCTIONS
        ##################

        def bruc_private_codes(upload_to):

            if os.path.isfile("/Volumes/MB/Brucella/Brucella Logsheets/ALL_WGS.xlsx"):
                private_location = "/Volumes/MB/Brucella/Brucella Logsheets/ALL_WGS.xlsx"
                print("private_location:  %s" % private_location)
                found = True

            elif os.path.isfile("/fdrive/Brucella/Brucella Logsheets/ALL_WGS.xlsx"):
                private_location = "/fdrive/Brucella/Brucella Logsheets/ALL_WGS.xlsx"
                print("private_location:  %s" % private_location)
                found = True

            else:
                print("Path to Brucella genotyping codes not found")

            if found:
                wb_out = xlsxwriter.Workbook(upload_to + "/brucella/genotyping_codes.xlsx")
                ws_out = wb_out.add_worksheet()

                wb_in = xlrd.open_workbook(private_location)

                row = 0
                col = 0

                sheet_in = wb_in.sheet_by_index(1)
                for row_data in sheet_in.col(32):
                    row_data = row_data.value
                    row_data = re.sub("/", "_", row_data)
                    row_data = re.sub("\.", "_", row_data)
                    row_data = re.sub("\*", "_", row_data)
                    row_data = re.sub("\?", "_", row_data)
                    row_data = re.sub("\(", "_", row_data)
                    row_data = re.sub("\)", "_", row_data)
                    row_data = re.sub("\[", "_", row_data)
                    row_data = re.sub("\]", "_", row_data)
                    row_data = re.sub(" ", "_", row_data)
                    row_data = re.sub("{", "_", row_data)
                    row_data = re.sub("}", "_", row_data)
                    row_data = re.sub("\'", "_", row_data)
                    row_data = re.sub("-_", "_", row_data)
                    row_data = re.sub("_-", "_", row_data)
                    row_data = re.sub("--", "_", row_data)
                    row_data = re.sub("_$", "", row_data)
                    row_data = re.sub("-$", "", row_data)
                    row_data = re.sub("\'", "", row_data)
                    row_data = str(row_data)

                    ws_out.write(row, col, row_data)
                    row += 1

                wb_out.close()

        def zip(src, dst):
            print ("\nZipping files...\n")
            zf = zipfile.ZipFile("%s.zip" % (dst), "w", zipfile.ZIP_DEFLATED)
            abs_src = os.path.abspath(src)
            for dirname, subdirs, files in os.walk(src):
                for filename in files:
                    absname = os.path.abspath(os.path.join(dirname, filename))
                    arcname = absname[len(abs_src) + 1:]
                    zf.write(absname, arcname)
            zf.close()

        # Test for duplicate samples
        def test_duplicate():
            dup_list = []
            list_of_files = glob.glob('*vcf')
            for line in list_of_files:
                line=re.sub(r'(.*)[_.].*', r'\1', line)
                dup_list.append(line)
            # find duplicates in list
            duplicates = [k for k,v in Counter(dup_list).items() if v>1]
            if len(duplicates) > 0:
                print ("Duplicates Found: %s " % duplicates)
                print ("\n***Error:  Duplicate VCFs")
                sys.exit(0)
            else:
                print ("\nno duplicate VCFs\n")

        # Change file names
        def change_names():
            code_dictionary = {}
            try:
                wb = xlrd.open_workbook(genotypingcodes)
                ws = wb.sheet_by_index(0)
                for rownum in range(ws.nrows):
                    new_name = str(ws.row_values(rownum)[0])
                    new_name = new_name.rstrip()
                    new_name = re.sub('[\/() ]', '_', new_name)
                    new_name = re.sub('#', 'num', new_name)
                    new_name = re.sub('_-', '_', new_name)
                    new_name = re.sub('-_', '_', new_name)
                    new_name = re.sub('__+', '_', new_name)
                    new_name = re.sub('_$', '', new_name)
                    new_name = re.sub('-$', '', new_name)
                    new_name = re.sub(',', '', new_name)
                    try:
                        elite_test = ws.row_values(rownum)[1]
                    except IndexError:
                        #print ("except IndexError: when changing names")
                        elite_test = ""
                    code_dictionary.update({new_name:elite_test})
            except FileNotFoundError:
                print ("\n#### except: FileNotFoundError, there was not a \"genotypingcodes\" file given to change names\n")

            names_not_changed = []
            list_of_files = glob.glob('*vcf')
            for each_vcf in list_of_files:
                vcf_found = False
                vcf_pretext = re.sub(r'(.*?)[._].*', r'\1', each_vcf) # ? was needed to make greedy, in my view the regex was searching right to left without it.
                vcf_pretext = vcf_pretext.rstrip()
                #if vcf_pretext[-1].isdigit():
                if len(vcf_pretext) < 8: # will catch all TB numbers
                    myregex = re.compile(vcf_pretext + '_.*') #if number require a underscore at end (writen with 16-0338, both TB and acc number, in mind)
                else:
                    myregex = re.compile(vcf_pretext + '.*') #if letter do not put a underscore at end (writen with MI in mind)
                for k, v in code_dictionary.items():
                    try:
                        if myregex.search(k):
                            os.rename(each_vcf, k + ".vcf")
                            vcf_found = True
                    except FileNotFoundError:
                        print ("except FileNotFoundError %s" % each_vcf)
                if vcf_found == False:
                            names_not_changed.append(each_vcf)
            names_not_changed = set(names_not_changed) # remove duplicates

            if options.elite:
                list_of_files = []
                list_of_files = glob.glob('*vcf')
                if not os.path.exists("temp_hold"):
                    print ("making temp_hold directory")
                    os.makedirs("temp_hold") # make all_vcfs if none exists
                for each_vcf in list_of_files:
                    time_test = time.time() - os.path.getmtime(each_vcf) < (1 * 24 * 60 *60) # 1day * (24*60*60)sec in day
                    print ("%s each_vcf" % each_vcf)
                    vcf_pretext = re.sub(r'(.*?)[._].*', r'\1', each_vcf) # ? was needed to make greedy, in my view the regex was searching right to left without it.
                    vcf_pretext = vcf_pretext.rstrip()
                    myregex = re.compile(vcf_pretext + '.*')
                    if time_test:
                        print ("time_test true %s" % each_vcf)
                        shutil.copy(each_vcf, "temp_hold")
                    else:
                        for k, v in code_dictionary.items():
                            if myregex.search(k):
                                try:
                                    print ("##### %s" % time_test)
                                    if v == "Yes": # if marked yes in column 2 of genotyping codes
                                        print ("marked yes %s" % each_vcf)
                                        shutil.copy(each_vcf, "temp_hold") # if "Yes" then moved to temp_hold
                                    else:
                                        print ("file will be discarded %s" % each_vcf)
                                except FileNotFoundError:
                                    print ("except FileNotFoundError %s" % each_vcf)
                        os.remove(each_vcf)
                shutil.rmtree('starting_files')
                os.makedirs('starting_files')
                os.renames('temp_hold', 'starting_files')
                list_of_files = glob.glob('starting_files/*vcf')
                file_number = len(list_of_files) # update the file_number to present on summary
                for each_vcf in list_of_files:
                    shutil.copy(each_vcf, root_dir)
                all_starting_files = glob.glob('*vcf')
                print (file_number)

            return names_not_changed

        # Table to Excel file
        def excelwriter(filename):
            orginal_name=filename
            filename = filename.replace(".txt",".xlsx")
            wb = xlsxwriter.Workbook(filename)
            ws = wb.add_worksheet("Sheet1")
            with open(orginal_name,'r') as csvfile:
                table = csv.reader(csvfile, delimiter='\t')
                i = 0
                for row in table:
                    ws.write_row(i, 0, row)
                    i += 1

            col = len(row)
            col = col + 1
            #print (i, "x", col)

            formatA = wb.add_format({'bg_color':'#58FA82'})
            formatG = wb.add_format({'bg_color':'#F7FE2E'})
            formatC = wb.add_format({'bg_color':'#0000FF'})
            formatT = wb.add_format({'bg_color':'#FF0000'})
            formatnormal = wb.add_format({'bg_color':'#FDFEFE'})
            formatlowqual = wb.add_format({'font_color':'#C70039', 'bg_color':'#E2CFDD'})
            formathighqual = wb.add_format({'font_color':'#000000', 'bg_color':'#FDFEFE'})
            formatambigous = wb.add_format({'font_color':'#C70039', 'bg_color':'#E2CFDD'})
            formatN = wb.add_format({'bg_color':'#E2CFDD'})

            ws.conditional_format(i-2,1,i-2,col-1, {'type':'text',
                                  'criteria':'containing',
                                  'value':60,
                                  'format':formathighqual})
            ws.conditional_format(i-2,1,i-2,col-1, {'type':'text',
                                'criteria':'containing',
                                'value':59,
                                'format':formathighqual})
            ws.conditional_format(i-2,1,i-2,col-1, {'type':'text',
                                'criteria':'containing',
                                'value':58,
                                'format':formathighqual})
            ws.conditional_format(i-2,1,i-2,col-1, {'type':'text',
                                'criteria':'containing',
                                'value':57,
                                'format':formathighqual})
            ws.conditional_format(i-2,1,i-2,col-1, {'type':'text',
                                'criteria':'containing',
                                'value':56,
                                'format':formathighqual})
            ws.conditional_format(i-2,1,i-2,col-1, {'type':'text',
                                'criteria':'containing',
                                'value':55,
                                'format':formathighqual})
            ws.conditional_format(i-2,1,i-2,col-1, {'type':'text',
                                'criteria':'containing',
                                'value':54,
                                'format':formathighqual})
            ws.conditional_format(i-2,1,i-2,col-1, {'type':'text',
                                'criteria':'containing',
                                'value':53,
                                'format':formathighqual})
            ws.conditional_format(i-2,1,i-2,col-1, {'type':'text',
                                'criteria':'containing',
                                'value':52,
                                'format':formathighqual})
            ws.conditional_format(i-2,1,i-2,col-1, {'type':'text',
                                'criteria':'containing',
                                'value':51,
                                'format':formathighqual})
            ws.conditional_format(i-2,1,i-2,col-1, {'type':'text',
                                'criteria':'containing',
                                'value':50,
                                'format':formathighqual})
            ws.conditional_format(i-2,1,i-2,col-1, {'type':'text',
                                'criteria':'not containing',
                                'value':100,
                                'format':formatlowqual})

            ws.conditional_format(2,1,i-3,col-1, {'type':'cell',
                                'criteria':'==',
                                'value':'B$2',
                                'format':formatnormal})
            ws.conditional_format(2,1,i-3,col-1, {'type':'text',
                                'criteria':'containing',
                                'value':'A',
                                'format':formatA})
            ws.conditional_format(2,1,i-3,col-1, {'type':'text',
                                'criteria':'containing',
                                'value':'G',
                                'format':formatG})
            ws.conditional_format(2,1,i-3,col-1, {'type':'text',
                                'criteria':'containing',
                                'value':'C',
                                'format':formatC})
            ws.conditional_format(2,1,i-3,col-1, {'type':'text',
                                'criteria':'containing',
                                'value':'T',
                                'format':formatT})
            ws.conditional_format(2,1,i-3,col-1, {'type':'text',
                                'criteria':'containing',
                                'value':'S',
                                'format':formatambigous})
            ws.conditional_format(2,1,i-3,col-1, {'type':'text',
                                'criteria':'containing',
                                'value':'Y',
                                'format':formatambigous})
            ws.conditional_format(2,1,i-3,col-1, {'type':'text',
                                'criteria':'containing',
                                'value':'R',
                                'format':formatambigous})
            ws.conditional_format(2,1,i-3,col-1, {'type':'text',
                                'criteria':'containing',
                                'value':'W',
                                'format':formatambigous})
            ws.conditional_format(2,1,i-3,col-1, {'type':'text',
                                'criteria':'containing',
                                'value':'K',
                                'format':formatambigous})
            ws.conditional_format(2,1,i-3,col-1, {'type':'text',
                                'criteria':'containing',
                                'value':'M',
                                'format':formatambigous})
            ws.conditional_format(2,1,i-3,col-1, {'type':'text',
                                'criteria':'containing',
                                'value':'N',
                                'format':formatN})
            ws.conditional_format(2,1,i-3,col-1, {'type':'text',
                                'criteria':'containing',
                                'value':'-',
                                'format':formatN})

            ws.set_column(0, 0, 30)
            ws.set_column(1, col-1, 2)
            ws.freeze_panes(2, 1)
            format_rotation = wb.add_format({'rotation':'90'})
            ws.set_row(0, 140, format_rotation)
            formatannotation = wb.add_format({'font_color':'#0A028C', 'rotation':'-90', 'align':'top'})
            #set last row
            ws.set_row(i-1, 400, formatannotation)

            wb.close()

        def get_annotations(all_positions):
            print ("Getting annotations")
            dict_annotation = {}
            in_annotation_as_dict = SeqIO.to_dict(SeqIO.parse(gbk_file, "genbank"))
            for each_absolute_pos in all_positions:
                pos_found = False
                each_absolute_pos = each_absolute_pos.split("-")
                chrom = each_absolute_pos[0]
                chrom.rstrip()
                #print ("chrom %s" % chrom)
                pos = each_absolute_pos[1]
                pos.rstrip()
                pos = int(pos)
                #print ("pos %s" % pos)
                for each_key, each_value in in_annotation_as_dict.items():
                    if chrom == each_key:
                        for feature in each_value.features:
                            if pos in feature and "CDS" in feature.type:
                                myproduct = "none list"
                                mylocus = "none list"
                                mygene = "none list"
                                for p in feature.qualifiers['product']:
                                    myproduct = p
                                for l in feature.qualifiers['locus_tag']:
                                    mylocus = l
                                if "gene" in feature.qualifiers:
                                    gene = feature.qualifiers['gene']
                                    for g in gene:
                                        mygene = g
                                myout = myproduct + ", gene: " + mygene + ", locus_tag: " + mylocus
                                pos_found = True
                if pos_found == False:
                    myout = "No annotated product"
                dict_annotation.update({chrom + "-" + str(pos):myout})
                #print ("myout %s" % myout)
            return (dict_annotation)

        def sort_table(intable, ordered, out_org):
            mytable = pd.read_csv(intable, sep='\t')
            mytable=mytable.set_index('reference_pos')

            # order list is from tree file
            # gives order for samples to be listed in table to be phylogenetically correct
            ordered_list = []
            with open(ordered) as infile:
                for i in infile:
                    i = i.rstrip()
                    ordered_list.append(i)
            # sinces this is set as the mytable index do not include in ordering
            ordered_list.remove('reference_pos')

            # reorder table based on order of list
            mytable = mytable.reindex(ordered_list)

            # count number of SNPs in each column
            snp_per_column = []
            for column_header in mytable:
                count = 0
                column = mytable[column_header]
                # for each element in the column
                for element in column:
                    if element != column[0]:
                        count = count + 1
                snp_per_column.append(count)
                #print ("the count is: %s" % count)
            row1 = pd.Series (snp_per_column, mytable.columns, name="snp_per_column")

            # get the snp count per column
            # for each column in the table
            snp_from_top = []
            for column_header in mytable:
                count = 0
                column = mytable[column_header]
                # for each element in the column
                # skip the first element
                for element in column[1:]:
                    if element == column[0]:
                        count = count + 1
                    else:
                        break
                snp_from_top.append(count)
                #print ("the count is: %s" % count)
            row2 = pd.Series (snp_from_top, mytable.columns, name="snp_from_top")

            mytable = mytable.append([row1])
            mytable = mytable.append([row2])

            mytable = mytable.T
            mytable = mytable.sort_values(['snp_from_top', 'snp_per_column'], ascending=[True, False])
            mytable = mytable.T

            # remove snp_per_column and snp_from_top rows
            mytable = mytable[:-2]
            mytable.to_csv(out_org, sep='\t')

        def find_filter_dict(each_vcf):
            dict_qual = {}
            dict_map = {}
            vcf_reader = vcf.Reader(open(each_vcf, 'r'))
            for record in vcf_reader:
                absolute_positon = str(record.CHROM) + "-" + str(record.POS)
                if record.QUAL:
                    returned_qual = []
                    returned_qual.append(record.QUAL)
                try:
                    returned_map = []
                    returned_map.append(record.INFO['MQ'])
                except KeyError:
                    pass
                
                dict_qual[absolute_positon] = returned_qual
                dict_map[absolute_positon] = returned_qual
            return dict_qual, dict_map

        test_duplicate() #***FUNCTION CALL

        try:
            mygbk = True
            print ("\tgbk_file: %s " % gbk_file)
        except NameError:
            mygbk = False
            print ("There is not a gbk file available")
        print ("\tdefiningSNPs: %s " % definingSNPs)
        print ("\texcelinfile: %s " % excelinfile)
        print ("\tremove_from_analysis: %s " % remove_from_analysis)
        print ("\tfilter_files: %s " % filter_files)
        print ("\tbioinfoVCF: %s \n" % bioinfoVCF)
        ###

        if os.path.isfile(genotypingcodes):
            print ("\nChanging the VCF names")
            names_not_changed = change_names() # check if genotypingcodes exist.  if not skip.

        files = glob.glob('*vcf')
        print ("REMOVING FROM ANALYSIS...")
        wb = xlrd.open_workbook(remove_from_analysis)
        ws = wb.sheet_by_index(0)
        for each_sample in ws.col_values(0):
            each_sample = str(each_sample)
            each_sample = re.sub(r'(.*?)[._].*', r'\1', each_sample)
            myregex = re.compile(each_sample + '.*') # create regular expression to search for in VCF list
            for i in files:
                if myregex.search(i):
                    print ("### --> %s removed from the analysis" % i)
                    try:
                        os.remove(i)
                    except FileNotFoundError:
                        print ("FileNotFoundError:")

        #malformed_list = []
        print ("CHECKING FOR EMPTY FILES...")
        files = glob.glob('*vcf')
        for i in files:
            if os.stat(i).st_size == 0:
                print ("### %s is an empty file and has been deleted" % i)
                error_list.append("File was empty %s" % i)
                os.remove(i)

        all_starting_files = glob.glob('starting_files/*vcf')
        file_number = len(all_starting_files)

        print ("SORTING FILES...")
        global defining_snps
        defining_snps = {}
        global inverted_position
        inverted_position = {}
        wb = xlrd.open_workbook(definingSNPs)
        ws = wb.sheet_by_index(0)

        for rownum in range(ws.nrows):
            position = ws.row_values(rownum)[1:][0]
            grouping = ws.row_values(rownum)[:1][0]
            # inverted positions will NOT be found in the passing positions
            # inverted positions are indicated in Defining SNPs by ending with "!"
            if position.endswith('!'):
                position = re.sub('!', '', position)
                inverted_position.update({position:grouping})
            else:
                defining_snps.update({position:grouping})
        files = glob.glob('*vcf')

        all_list_amb = {}
        group_calls_list = []

        print ("Grouping files...")
        if options.debug_call:
            for i in files:
                dict_amb, group_calls, malformed = group_files(i)
                all_list_amb.update(dict_amb)
                group_calls_list.append(group_calls)
                error_list.append(malformed)
        else:
            with futures.ProcessPoolExecutor() as pool:
                for dict_amb, group_calls, malformed in pool.map(group_files, files):
                    all_list_amb.update(dict_amb)
                    group_calls_list.append(group_calls) # make list of list
                    error_list.append(malformed)
        error_list = [x for x in error_list if x] # remove empty sets from list

        print ("Getting directory list\n")
        directory_list = next(os.walk('.'))[1] # get list of subdirectories
        directory_list.remove('starting_files')

        print ("Getting SNPs in each directory")
        if options.debug_call:
            for i in directory_list:
                get_snps(i)
        else:
            with futures.ProcessPoolExecutor(max_workers=cpu_count) as pool:
                pool.map(get_snps, directory_list)

        runtime = (datetime.now() - startTime)
        print ("\n\nruntime: %s:  \n" % runtime)

        #############################################
        #MAKE HTML FILE:
        print ("<html>\n<head><style> table { font-family: arial, sans-serif; border-collapse: collapse; width: 40%; } td, th { border: 1px solid #dddddd; padding: 4px; text-align: left; font-size: 11px; } </style></head>\n<body style=\"font-size:12px;\">", file=htmlfile)
        print ("<h2>Script ran using <u>%s</u> variables</h2>" % options.species.upper(), file=htmlfile)
        print ("<h4>There are %s VCFs in this run</h4>" % file_number, file=htmlfile)

        #OPTIONS
        print ("Additional options ran: email: %s, options.filter: %s, all_vcf: %s, elite: %s, debug: %s, uploaded: %s" % (options.email, options.filter, options.all_vcf, options.elite, options.debug_call, options.upload), file=htmlfile)
        if options.all_vcf:
            print ("\n<h4>All_VCFs is available</h4>", file=htmlfile)
        elif options.elite:
            print ("\n<h4>Elite VCF comparison available</h4>", file=htmlfile)

        #TIME
        print ("\n<h4>Start time: %s <br>" % startTime, file=htmlfile)
        print ("End time: %s <br>" % datetime.now(), file=htmlfile)
        print ("Total run time: %s: </h4>" % runtime, file=htmlfile)

        # ERROR LIST
        if len(error_list) < 1:
            print ("<h2>No corrupt VCF removed</h2>", file=htmlfile)

        else:
            print ("\n<h2>Corrupt VCF removed</h2>", file=htmlfile)
            for i in error_list:
                print ("%s <br>" % i, file=htmlfile)
            print ("<br>", file=htmlfile)

        # AMBIGIOUS DEFINING SNPS
        if len(all_list_amb) < 1:
            print ("\n<h2>No ambiguous defining SNPs</h2>", file=htmlfile)
        else:
            print ("\n<h2>Defining SNPs are ambiguous.  They may be mixed isolates.</h2>", file=htmlfile)
            print ("<table>", file=htmlfile)
            print ("<tr align=\"left\"><th>Sample Name</th><th>Division</th><th>Absolute Position</th><tr>", file=htmlfile)
            ordered_all_list_amb = OrderedDict(sorted(all_list_amb.items()))
            for k, v in ordered_all_list_amb.items():
                k_split = k.split('\t')
                print ("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (k_split[0], k_split[1], v), file=htmlfile)
            print ("</table>", file=htmlfile)
            print ("<br>", file=htmlfile)

        #GROUPING TABLE
        print ("<h2>Groupings</h2>", file=htmlfile)
        print ("<table>", file=htmlfile)
        print ("<tr align=\"left\"><th>Sample Name</th><tr>", file=htmlfile)

        group_calls_list = list(filter(None, group_calls_list))
        try:
            group_calls_list.sort(key=lambda x: x[0]) # sort list of list by first element
        except IndexError:
            print("Unable to sort grouping list")
            pass

        for i in group_calls_list:
            print ("<tr>", file=htmlfile)
            for x in i:
                print ("<td>%s</td>" % x, end='\t', file=htmlfile)
            print ("</tr>", file=htmlfile)
        print ("</table>", file=htmlfile)

        #FILES NOT RENAMED
        if names_not_changed:
            print ("\n<h2>File names did not get changed:</h2>", file=htmlfile)
            for i in sorted(names_not_changed):
                print ("%s<br>" % i, file=htmlfile)

        print ("</body>\n</html>", file=htmlfile)
        #############################################
        os.chdir(root_dir)
        zip("starting_files", "starting_files") # zip starting files directory
        shutil.rmtree("starting_files")

        htmlfile.close()

        ####send email:
        def send_email():
            print ("Sending Email...")
            print ("Sending to:")

            msg = MIMEMultipart()
            msg['From'] = "tod.p.stuber@aphis.usda.gov"
            msg['To'] = email_list
            msg['Subject'] = "Script 2 " + options.species
            with open(htmlfile_name) as fp:
                msg.attach(MIMEText(fp.read(), 'html'))

            part = MIMEBase('application', "octet-stream")
            part.set_payload(open("summary_log.html", "r").read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="summary_log.html"')
            msg.attach(part)

            smtp = smtplib.SMTP('10.10.8.12')
            smtp.send_message(msg)

            #smtp.send_message(msg)
            #smtp.send_message(msg.as_string())
            #smtp.sendmail(email_list, msg.as_string())
            #smtp.sendmail("tod.p.stuber@aphis.usda.gov", email_list, msg.as_string())
            smtp.quit()

        if options.email == "none":
            print ("\n\temail not sent")
        elif options.email:
            send_email()
            print ("\n\temail sent to: %s" % email_list)
        else:
            print ("\n\temail not sent")

        if options.upload:
            print ("Uploading Samples...")
            def copytree(src, dst, symlinks=False, ignore=None): #required to ignore permissions
                try:
                    for item in os.listdir(src):
                        s = os.path.join(src, item)
                        d = os.path.join(dst, item)
                        try:
                            if os.path.isdir(s):
                                shutil.copytree(s, d, symlinks, ignore)
                            else:
                                shutil.copy2(s, d)
                        except shutil.Error:
                            pass
                except FileNotFoundError:
                    print ("except FileNotFoundError: file not found")

            #upload to bioinfoVCF
            src = root_dir
            dst = bioinfoVCF + "/" + os.path.basename(os.path.normpath(root_dir))
            print ("\n\t%s is copying to %s" % (src, dst))
            os.makedirs(dst, exist_ok=True)
            copy_tree(src, dst, preserve_mode=0, preserve_times=0)

        print ("\n\tDONE\n")
        #xvfb.kill

        if vdisplay_status:
            vdisplay.stop()

###############################################
###############################################
###################map pooled##################
###############################################
###############################################

#map pooled from script 1
def read_aligner(directory):
    os.chdir(directory)
    R1 = glob.glob('*_R1*fastq.gz')
    R2 = glob.glob('*_R2*fastq.gz')
    print("R1 and R2: %s %s" % (R1, R2))
    if options.species:
        sample = script1(R1[0], R2[0], options.species) #force species
    else:
        sample = script1(R1[0], R2[0]) #no species give, will find best
    stat_summary = sample.align_reads()
    return(stat_summary)

# Group files, map pooled from script 2
def group_files(each_vcf):
    list_pass = []
    list_amb = []
    dict_amb = {}
    malformed = []
    group_calls = []
    passing = True
    print("qual_gatk_threshold: %s " % qual_gatk_threshold)
    ###
    # Fix common VCF errors
    if options.debug_call:
        print ("FIXING FILE: " + each_vcf)
    temp_file = each_vcf + ".temp"
    write_out=open(temp_file, 'w') #r+ used for reading and writing to the same file

    with open(each_vcf, 'r') as file:
        try:
            for line in file:
                if line.rstrip(): # true if not empty line'^$'
                    line = line.rstrip() #remove right white space
                    line = re.sub('"AC=', 'AC=', line)
                    line = re.sub('""', '"', line)
                    line = re.sub('"$', '', line)
                    line = re.sub('GQ:PL\t"', 'GQ:PL\t', line)
                    line = re.sub('[0-9]+\tGT\t.\/.$', '999\tGT:AD:DP:GQ:PL\t1/1:0,80:80:99:2352,239,0', line)
                    line = re.sub('^"', '', line)
                    if line.startswith('##'):
                        line = line.split('\t')
                        line = ''.join(line[0])
                    if not line.startswith('##'):
                        line = re.sub('"', '', line)
                        line = line.split('\t')
                        line = "\t".join(line[0:10])
                        print(line, file=write_out)
                    else:
                        print(line, file=write_out)
        except IndexError:
            print ("##### IndexError: Deleting corrupt VCF file: " + each_vcf)
            malformed = "##### IndexError: Deleting corrupt VCF file: " + each_vcf
            os.remove(each_vcf)
        except UnicodeDecodeError:
            print ("##### UnicodeDecodeError: Deleting corrupt VCF file: " + each_vcf)
            malformed = "##### UnicodeDecodeError: Deleting corrupt VCF file: " + each_vcf
            os.remove(each_vcf)
            
    write_out.close()
    os.rename(temp_file, each_vcf)
    ###
    
    try:
        vcf_reader = vcf.Reader(open(each_vcf, 'r'))
        ### PUT VCF NAME INTO LIST, capturing for htmlfile
        group_calls.append(each_vcf)
            # for each single vcf getting passing position
        for record in vcf_reader:
            chrom = record.CHROM
            position = record.POS
            absolute_positon = str(chrom) + "-" + str(position)
            # find quality SNPs and put absolute positions into list
            try:
                record_alt_length = len(record.ALT[0])
            except TypeError:
                record_alt_length = 0
            try:
                record_ref_length = len(record.REF)
            except TypeError:
                record_alt_length = 0
            try:
                if str(record.ALT[0]) != "None" and record_ref_length == 1 and record_alt_length == 1 and record.INFO['AC'][0] == 2 and record.QUAL > qual_gatk_threshold and record.INFO['MQ'] > 45:
                    list_pass.append(absolute_positon)
                # capture ambigous defining SNPs in htmlfile
                elif str(record.ALT[0]) != "None" and record.INFO['AC'][0] == 1:
                    list_amb.append(absolute_positon)
            except ZeroDivisionError:
                print ("bad line in %s at %s" % (each_vcf, absolute_positon))

        for key in inverted_position.keys():
            if key not in list_pass:
                print ("key %s not in list_pass" % key)
                directory = inverted_position[key]
                print("*** INVERTED POSITION FOUND *** PASSING POSTION FOUND: \t%s\t\t%s" % (each_vcf, directory))
                if not os.path.exists(directory):
                    try:
                        os.makedirs(directory)
                    except FileExistsError:
                        null = "null"
                shutil.copy(each_vcf, directory)
                ### ADD GROUP TO LIST
                group_calls.append(directory)

        #if passing:
        # if a passing position is in the defining SNPs
        for passing_position in list_pass:
            # normal grouping
            if passing_position in defining_snps:
                directory = defining_snps[passing_position]
                print("PASSING POSTION FOUND: \t%s\t\t%s" % (each_vcf, directory))
                if not os.path.exists(directory):
                    try:
                        os.makedirs(directory)
                    except FileExistsError:
                        null = "null"
                shutil.copy(each_vcf, directory)
                ### ADD GROUP TO LIST
                group_calls.append(directory)
                
        # find mixed isolates if defining snp is ambigous
        for amb_position in list_amb:
            if amb_position in defining_snps:
                directory = defining_snps[amb_position]
                dict_amb.update({each_vcf + "\t" + directory:amb_position})
                ### ADD AMBIGIOUS CALL TO LIST
                group_calls.append("*" + directory + "-mix")
        # if -a or -e (non elites already deleted from the analysis) copy all vcfs to All_VCFs
        if options.all_vcf or options.elite:
            if not os.path.exists("All_VCFs"):
                os.makedirs("All_VCFs")
            shutil.move(each_vcf, "All_VCFs")
        else:
            try:
                os.remove(each_vcf)
            except FileNotFoundError:
                print ("file deleted: %s " % each_vcf)
                malformed.append(each_vcf)
        #print (dict_amb, group_calls, malformed)
        
        try:
            some_object_iterator = iter(group_calls)
        except TypeError:
            group_calls = []

        try:
            some_object_iterator = iter(dict_amb)
        except TypeError:
            dict_amb = {}

        try:
            some_object_iterator = iter(malformed)
        except TypeError:
            os.remove(each_vcf)
            print ("TypeError: corrupt VCF, removed %s " % each_vcf)
            malformed = "TypeError: corrupt VCF, removed %s " % each_vcf

    except ZeroDivisionError:
        os.remove(each_vcf)
        print ("ZeroDivisionError: corrupt VCF, removed %s " % each_vcf)
        malformed = "ZeroDivisionError: corrupt VCF, removed %s " % each_vcf
    except ValueError:
        os.remove(each_vcf)
        print ("ValueError: corrupt VCF, removed %s " % each_vcf)
        malformed = "ValueError: corrupt VCF, removed %s " % each_vcf
    except UnboundLocalError:
        os.remove(each_vcf)
        print ("UnboundLocalError: corrupt VCF, removed %s " % each_vcf)
        malformed = "UnboundLocalError: corrupt VCF, removed %s " % each_vcf
    except TypeError:
        os.remove(each_vcf)
        print ("TypeError: corrupt VCF, removed %s " % each_vcf)
        malformed = "TypeError: corrupt VCF, removed %s " % each_vcf
    except SyntaxError:
        os.remove(each_vcf)
        print ("SyntaxError: corrupt VCF, removed %s " % each_vcf)
        malformed = "SyntaxError: corrupt VCF, removed %s " % each_vcf
    except KeyError:
        os.remove(each_vcf)
        print ("KeyError: corrupt VCF, removed %s " % each_vcf)
        malformed = "KeyError: corrupt VCF, removed %s " % each_vcf
    except StopIteration:
        print ("StopIteration: %s" % each_vcf)
        malformed = "KeyError: corrupt VCF, removed %s " % each_vcf

    a = group_calls[0:1]
    b = sorted(group_calls[1:]) # order the groups
    for i in b:
        a.append(i) # a is group_calls
        group_calls = a
    return dict_amb, group_calls, malformed

# Group files, map pooled from script 2
def find_positions(filename):
    found_positions = {}
    vcf_reader = vcf.Reader(open(filename, 'r'))
    try:
        for record in vcf_reader:
            chrom = record.CHROM
            position = record.POS
            absolute_positon = str(chrom) + "-" + str(position)
            filter=record.FILTER
            
            # Usable positins are those that:

            # ADD PARAMETERS HERE TO CHANGE WHAT'S SNP WILL BE USED
            # IF NOT FOUND HERE THE SNP WILL BE IGNORED.  WILL NOT BE REPRESENTED.  HARD REMOVAL
            
            ## GATK parameters
            # str(record.ALT[0]) != "None" --> filter deletions
            # len(record.REF) == 1 --> filter bad ref call with 2 nt present
            # len(record.ALT[0]) == 1 --> filter bad alt call with 2 nt present
            # record.heterozygosity == 0.0 --> filter AC=1, heterozygosity.
            # record.QUAL > 150 --> filter poor quality
            # record.INFO['MQ'] --> filter low map quality
            try:
                if str(record.ALT[0]) != "None" and record.INFO['AC'][0] == 2 and len(record.REF) == 1 and record.QUAL > qual_gatk_threshold:
                    found_positions.update({absolute_positon:record.REF})
            except KeyError:
                pass
    except ZeroDivisionError:
        print ("ZeroDivisionError error found")
    except ValueError:
        print ("ValueError error found")
    except UnboundLocalError:
        print ("UnboundLocalError error found")
    except TypeError:
        print ("TypeError error found")
    return found_positions

def get_snps(directory):
    os.chdir(root_dir+ "/" + directory)
    print ("\n----------------------------")
    print ("\nworking on: %s " % directory)
    outdir=str(os.getcwd()) + "/"
    # FILTER position all list
    list_filter_files = glob.glob(filter_files + '/*')

    filter_file = "empty" # if filter an all_vcf file not found mark as empty
    filter_group = "empty" # if a group specific filter file is not found mark as empty
    for i in list_filter_files:
        if "-All.txt" in i:
            filter_file = i

    for i in list_filter_files:
        if directory  + ".txt" in i:
            filter_group = i

    print ("%s --> filter_file %s " % (directory, filter_file))
    print ("%s --> filter_group %s " % (directory, filter_group))
    print ("%s --> outdir %s " % (directory, outdir))

    files = glob.glob('*vcf')
    all_positions = {}

    if options.debug_call:
        for i in files:
            found_positions = find_positions(i)
            all_positions.update(found_positions)
    else:
        with futures.ProcessPoolExecutor(max_workers=cpu_count) as pool:
            for found_positions in pool.map(find_positions, files):
                all_positions.update(found_positions)

    print ("Directory %s found positions %s" % (directory, len(all_positions)))
    presize=len(all_positions)

    # Filter applied to all positions
    if not filter_file is "empty":
        with open(filter_file, 'rt') as f:
            filter_list = f.read().splitlines() #removes \n
        for pos in filter_list:
            all_positions.pop(pos, None)
        f.close()

    # Filter applied to group
    if not filter_group is "empty":
        with open(filter_group, 'rt') as f:
            filter_list = f.read().splitlines() #removes \n
        for pos in filter_list:
            all_positions.pop(pos, None)
        f.close()

    print ("\nDirectory: ", directory)
    print ("Total positions found: %s" % format(presize, ",d"))
    print ("Possible positions filtered %s" % format(len(filter_list), ",d"))
    print ("Positions after filtering %s\n" % format(len(all_positions), ",d"))

    # NEEDS TO BE FIXED
    if options.filter:
        #write to files
        positions_to_filter = "positions_to_filter.txt"
        positions_to_filter_details = "positions_to_filter_details.txt"
        write_out_positions=open(positions_to_filter, 'w')
        write_out_details=open(positions_to_filter_details, 'w')

        files = glob.glob('*vcf')

        #calculate mean/max qual and map at all possible positions
        from collections import defaultdict
        dd_qual = {}
        dd_map = {}
        if options.debug_call:
            for each_vcf in files:
                print ("working on: %s" % each_vcf)
                dict_qual, dict_map = find_filter_dict(each_vcf)
                keys = set(dd_qual).union(dict_qual)
                no = []
                dd_qual = dict((k, dd_qual.get(k, no) + dict_qual.get(k, no)) for k in keys)
                keys = set(dd_map).union(dict_map)
                no = []
                dd_map = dict((k, dd_map.get(k, no) + dict_map.get(k, no)) for k in keys)
        else:
            with futures.ProcessPoolExecutor() as pool:
                for dict_qual, dict_map in pool.map(find_filter_dict, files):
                    keys = set(dd_qual).union(dict_qual)
                    no = []
                    dd_qual = dict((k, dd_qual.get(k, no) + dict_qual.get(k, no)) for k in keys)
                    keys = set(dd_map).union(dict_map)
                    no = []
                    dd_map = dict((k, dd_map.get(k, no) + dict_map.get(k, no)) for k in keys)

        #dict_qual=dict((k, v) for k, v in dict_qual.items() if v)
        #dict_map=dict((k, v) for k, v in dict_map.items() if v)

        ave_qual = {}
        max_qual = {}
        for k, v in dd_qual.items():
            #only use if > 3 positions have been called
            if len(v) > 3:
                ave_qual[k]=np.mean(v)
                max_qual[k]=np.max(v)

        ave_map = {}
        max_map = {}
        for k, v in dd_map.items():
            if len(v) > 3:
                ave_map[k]=np.mean(v)
                max_map[k]=np.max(v)		

        # get all possible used positions
        all_maybe_filter = []
        for k in ave_qual.keys():
            all_maybe_filter.append(k)
        for k in max_qual.keys():
            all_maybe_filter.append(k)
        for k in ave_map.keys():
            all_maybe_filter.append(k)
        for k in max_map.keys():
            all_maybe_filter.append(k)
            # remove duplicates
            all_maybe_filter = list(set(all_maybe_filter))

        #remove those in filter list
        #Filter applied to all positions
        if not filter_file is "empty":
            with open(filter_file, 'rt') as f:
                filter_list = f.read().splitlines() #removes \n
                try:
                    for pos in filter_list:
                        all_maybe_filter.pop(pos)
                except TypeError:
                    pass
                except KeyError:
                    pass
            f.close()

        # Filter applied to group
        if not filter_group is "empty":
            with open(filter_group, 'rt') as f:
                filter_list = f.read().splitlines() #removes \n
                try:
                    for pos in filter_list:
                        all_maybe_filter.pop(pos)
                except TypeError:
                    pass
                except KeyError:
                    pass
            f.close()

        # for each possible posible position check if to filter.
        for absolute_positon in all_maybe_filter:
            ave_qual_value = ave_qual[absolute_positon]
            max_qual_value = max_qual[absolute_positon]
            ave_map_value = ave_map[absolute_positon]
            max_map_value = max_map[absolute_positon]
            print ("%s, max_qual_value: %s, ave_qual_value: %s, max_map_value: %s, ave_map_value: %s" % (absolute_positon, max_qual_value, ave_qual_value, max_map_value, ave_map_value))
            if max_qual_value < 1300 and ave_qual_value < 800 and max_map_value < 58 and ave_map_value < 40:
                print ("%s, max_qual_value: %s, ave_qual_value: %s, max_map_value: %s, ave_map_value: %s" % (absolute_positon, max_qual_value, ave_qual_value, max_map_value, ave_map_value), file=write_out_details)
                print (absolute_positon, file=write_out_positions)
        write_out_positions.close()
        write_out_details.close()

    if mygbk:
        dict_annotation = get_annotations(all_positions)
        write_out=open('annotations.txt', 'w+')
        print ('reference_pos\tannotations', file=write_out)
        for k, v in dict_annotation.items():
            print ('%s\t%s' % (k, v), file=write_out)
        write_out.close()


    out_table= outdir + directory + "-table.txt"
    table=open(out_table, 'wt')

    # write absolute positions to table
    # order before adding to file to match with ordering of individual samples below
    all_positions=OrderedDict(sorted(all_positions.items()))
    print ("reference_pos", end="\t", file=table)
    for k, v in all_positions.items():
        print(k, end="\t", file=table)
    print ("", file=table)

    list_of_files = glob.glob('*vcf')

    # for each vcf
    all_map_qualities={}
    for file_name in list_of_files:
        sample_map_qualities={}
        just_name = file_name.replace('.vcf', '')
        just_name = re.sub('\..*', '*', just_name) # if after the .vcf is removed there is stilll a "." in the name it is assumed the name did not get changed
        print(just_name, end="\t", file=table)
        # for each line in vcf
        vcf_reader = vcf.Reader(open(file_name, 'r'))
        sample_dict = {}
        for record in vcf_reader:
            record_position = str(record.CHROM) + "-" + str(record.POS)
            if record_position in all_positions:
                #print ("############, %s, %s" % (file_name, record_position))
                # NOT SURE THIS IS THE BEST PLACE TO CAPTURE MQ AVERAGE
                # MAY BE FASTER AFTER PARSIMONY SNPS ARE DECIDED, BUT THEN IT WILL REQUIRE OPENING THE FILES AGAIN.
                if str(record.ALT[0]) != "None" and str(record.INFO['MQ']) != "nan": #on rare occassions MQ gets called "NaN" thus passing a string when a number is expected when calculating average.
                    #print ("getting map quality:    %s          %s      %s" % (record.INFO['MQ'], file_name, str(record.POS)))
                    sample_map_qualities.update({record_position:record.INFO['MQ']})
                # ADD PARAMETERS HERE TO CHANGE WHAT'S EACH VCF REPRESENTS.
                # SNP IS REPRESENTED IN TABLE, NOW HOW WILL THE VCF REPRESENT THE CALLED POSITION
                # str(record.ALT[0]) != "None", which means a deletion as ALT
                # not record.FILTER, or rather PASSED.
                
                # check record.QUAL
                # In GATK VCFs "!= None" not used.
                if str(record.ALT[0]) != "None" and len(record.ALT[0]) == 1 and record.INFO['AC'][0] == 2:
                    sample_dict.update({record_position:record.ALT[0]})
                # same as above but take into account Ambiguious call
                #elif str(record.ALT[0]) != "None" and len(record.ALT[0]) == 1 and record.INFO['AC'][0] == 1 and record.QUAL >= N_gatk_threshold:
                elif str(record.ALT[0]) != "None" and len(record.ALT[0]) == 1 and record.INFO['AC'][0] == 1:
                    ref_alt = str(record.ALT[0]) + str(record.REF[0])
                    if ref_alt == "AG":
                        sample_dict.update({record_position:"R"})
                    elif ref_alt == "CT":
                        sample_dict.update({record_position:"Y"})
                    elif ref_alt == "GC":
                        sample_dict.update({record_position:"S"})
                    elif ref_alt == "AT":
                        sample_dict.update({record_position:"W"})
                    elif ref_alt == "GT":
                        sample_dict.update({record_position:"K"})
                    elif ref_alt == "AC":
                        sample_dict.update({record_position:"M"})
                    elif ref_alt == "GA":
                        sample_dict.update({record_position:"R"})
                    elif ref_alt == "TC":
                        sample_dict.update({record_position:"Y"})
                    elif ref_alt == "CG":
                        sample_dict.update({record_position:"S"})
                    elif ref_alt == "TA":
                        sample_dict.update({record_position:"W"})
                    elif ref_alt == "TG":
                        sample_dict.update({record_position:"K"})
                    elif ref_alt == "CA":
                        sample_dict.update({record_position:"M"})
                    else:
                        sample_dict.update({record_position:"N"})
                    # Poor calls
                elif str(record.ALT[0]) != "None" and record.QUAL < N_gatk_threshold:
                    sample_dict.update({record_position:"N"})
                # same as above but take into account Deletion call
                elif str(record.ALT[0]) == "None":
                    sample_dict.update({record_position:"-"})

        # After iterating through VCF combine dict to nested dict
        all_map_qualities.update({just_name: sample_map_qualities})

        # merge dictionaries and order
        merge_dict={}
        merge_dict.update(all_positions)
        merge_dict.update(sample_dict)
        merge_dict=OrderedDict(sorted(merge_dict.items()))
        for k, v in merge_dict.items():
            #print ("k %s, v %s" % (k, v))
            print (str(v) + "\t", file=table, end="")
        print ("", file=table)
    table.close()

    ## Select parsimony informative SNPs
    mytable = pd.read_csv(out_table, sep='\t')
    mytable = mytable.set_index('reference_pos')

    # drop NaN rows and columns
    mytable=mytable.dropna(axis=1)

    # SELECT PARISOMONY INFORMATIVE SNPSs
    # removes columns where all fields are the same
    parsimony=mytable.loc[:, (mytable != mytable.ix[0]).any()]
    parsimony_positions=list(parsimony)

    write_out=open("each_vcf-poslist.txt", 'wt')
    for i in parsimony_positions:
        write_out.write(i + "\n") # writing to each_vcf-poslist.txt
    write_out.close()

    parsimony.to_csv(out_table, sep="\t", index_label='reference_pos')
    table=open(out_table, 'a')

    # added corresponding reference to parsimony table
    print ("reference_call", end="\t", file=table)
    all_positions_list=list(all_positions)
    for l in parsimony_positions:
        print(all_positions.get(l), end="\t", file=table)
    print ("", file=table)
    table.close()

    # fix end, NEED TO REWRITE, WRITING TO NEW FILE IS CLUNKY FIX
    write_table= outdir + directory + "-write.txt"
    write_out=open(write_table, 'wt')
    with open(out_table, 'rt') as f:
        for line in f:
            line = line.replace('\t\n', '\n')
            print (line, file=write_out)
    write_out.close()

    #Print out fasta alignment file from table
    alignment_file= outdir + directory + ".fasta"
    write_out=open(alignment_file, 'wt')
    with open(out_table, 'rt') as f:
        count=0
        for line in f:
            if count > 0:
                line=re.sub('^', '>', line)
                line=line.replace('reference_call', 'root')
                line=line.replace('\t', '\n', 1)
                line=line.replace('\t', '')
                print (line, end="", file=write_out)
            count = count + 1
    write_out.close()

    mytable = pd.read_csv(write_table, sep='\t')
    mytable = mytable.set_index('reference_pos')
    mytable=mytable.dropna(axis=1)

    os.remove(write_table)

    # move reference to top row
    myref=mytable[-1:]
    myother=mytable[:-1]
    frames = [myref, myother]
    mytable=pd.concat(frames)
    mytable.to_csv(out_table, sep="\t", index_label='reference_pos')

    print ("\n%s table dimensions: %s" % (directory, str(mytable.shape)))

    print ("%s RAxML running..." % directory)
    rooted_tree = outdir + directory + "-rooted.tre"
    os.system("{} -s {} -n raxml -m GTRCATI -o root -p 12345 -T {} > /dev/null 2>&1" .format(sys_raxml, alignment_file, raxml_cpu))

    try:
        ordered_list_from_tree = outdir + directory + "-cleanedAlignment.txt"
        write_out=open(ordered_list_from_tree, 'w+')
        print ("reference_pos", file=write_out)
        print ("reference_call", file=write_out)
        if os.path.isfile("RAxML_bestTree.raxml"):
            with open("RAxML_bestTree.raxml", 'rt') as f:
                for line in f:
                    line=re.sub('[:,]', '\n', line)
                    line=re.sub('[)(]', '', line)
                    line=re.sub('[0-9].*\.[0-9].*\n', '', line)
                    line=re.sub('root\n', '', line)
                    write_out.write(line)
            os.rename("RAxML_bestTree.raxml", "RAxML_bestTree.raxml.tre")
            write_out.close()

        out_org = outdir + directory + "-organized-table.txt"

        sort_table(out_table, ordered_list_from_tree, out_org) #function

        print ("%s Getting map quality..." % directory)
        average=lambda x: x.mean()
        all_map_qualities=pd.DataFrame(all_map_qualities)
        #ave_mq = Type: Series
        ave_mq = all_map_qualities.apply(average, axis=1)
        ave_mq = ave_mq.astype(int)
        ave_mq.to_csv('outfile.txt', sep='\t') # write to csv

        write_out=open('map_quality.txt', 'w+')
        print ('reference_pos\tmap-quality', file=write_out)
        with open('outfile.txt', 'rt') as f:
            for line in f:
                write_out.write(line)
        write_out.close()
        #os.remove('outfile.txt')

        #add_map_qualities() #***FUNCTION CALL
        #seemed pooling did not like a function with no parameters given
        quality = pd.read_csv('map_quality.txt', sep='\t')

        mytable = pd.read_csv(out_table, sep='\t')
        mytable=mytable.set_index('reference_pos')

        # order list is from tree file
        # gives order for samples to be listed in table to be phylogenetically correct
        ordered_list = []
        with open(ordered_list_from_tree) as infile:
            for i in infile:
                i = i.rstrip()
                ordered_list.append(i)
        # sinces this is set as the mytable index do not include in ordering
        ordered_list.remove('reference_pos')

        # reorder table based on order of list
        mytable = mytable.reindex(ordered_list)
        mytable.to_csv(out_table, sep='\t')

        out_sort=str(os.getcwd()) + "/" + directory + "-sorted-table.txt" #sorted
        mytable_sort = pd.read_csv(out_table, sep='\t') #sorted
        mytable_sort = mytable_sort.set_index('reference_pos') #sorted
        mytable_sort = mytable_sort.transpose() #sort
        mytable_sort.to_csv(out_sort, sep='\t', index_label='reference_pos') #sort

        out_org=str(os.getcwd()) + "/" + directory + "-organized-table.txt" #org
        mytable = pd.read_csv(out_org, sep='\t') #org
        mytable = mytable.set_index('reference_pos') #org
        mytable = mytable.transpose() #org
        mytable.to_csv(out_org, sep='\t', index_label='reference_pos') #org

        if mygbk:
            print ("%s gbk is present, getting annotation...\n" % directory)
            annotations = pd.read_csv('annotations.txt', sep='\t') #sort
            mytable_sort = pd.read_csv(out_sort, sep='\t') #sort
            mytable_sort = mytable_sort.merge(quality, on='reference_pos', how='inner') #sort
            mytable_sort = mytable_sort.merge(annotations, on='reference_pos', how='inner') #sort
            mytable_sort = mytable_sort.set_index('reference_pos') #sort
            mytable_sort = mytable_sort.transpose() #sort
            mytable_sort.to_csv(out_sort, sep='\t', index_label='reference_pos') #sort

            #annotations = pd.read_csv('annotations.txt', sep='\t') #org
            mytable = pd.read_csv(out_org, sep='\t') #org
            mytable = mytable.merge(quality, on='reference_pos', how='inner') #org
            mytable = mytable.merge(annotations, on='reference_pos', how='inner') #org
            mytable = mytable.set_index('reference_pos') #org
            mytable = mytable.transpose() #org
            mytable.to_csv(out_org, sep='\t', index_label='reference_pos') #org

        else:
            print ("No gbk file or no table to annotate")
            mytable_sort = pd.read_csv(out_sort, sep='\t') #sort
            mytable_sort = mytable_sort.merge(quality, on='reference_pos', how='inner') #sort
            mytable_sort = mytable_sort.set_index('reference_pos') #sort
            mytable_sort = mytable_sort.transpose() #sort
            mytable_sort.to_csv(out_sort, sep='\t', index_label='reference_pos') #sort
            # add when no annotation
            with open(out_sort, 'rt') as f:
                line=f.readline()
            f.close()
            column_count = line.count('\t') #sort
            column_count = column_count - 1 #sort
            #print ("column_count: %s" % column_count)
            with open(out_sort, 'at') as f:
                print ("no_annotation", end = '', file=f)
                print ('\t' * column_count, file=f)
            f.close()

            print ("No gbk file or no table to annotate")
            mytable = pd.read_csv(out_org, sep='\t') #org
            mytable = mytable.merge(quality, on='reference_pos', how='inner') #org
            mytable = mytable.set_index('reference_pos') #org
            mytable = mytable.transpose() #org
            mytable.to_csv(out_org, sep='\t', index_label='reference_pos') #org
            # add when no annotation
            with open(out_org, 'rt') as f:
                line=f.readline()
            f.close()
            column_count = line.count('\t')
            column_count = column_count - 1
            #print ("column_count: %s" % column_count)
            with open(out_org, 'at') as f:
                print ("no_annotation", end = '', file=f)
                print ('\t' * column_count, file=f)
            f.close()
        
        excelwriter(out_sort) #***FUNCTION CALL #sort
        excelwriter(out_org) #***FUNCTION CALL #org

        for r in glob.glob('*vcf'):
            os.remove(r)

    except ValueError:
        print ("##### ValueError: %s #####" % file_name)
        return
    try:
        os.remove(ordered_list_from_tree)
        os.remove('each_vcf-poslist.txt')
        os.remove('map_quality.txt')
        if mygbk:
            os.remove("annotations.txt")
        os.remove("outfile.txt")
        os.remove(out_sort)
        os.remove(out_org) # organized.txt table
        os.remove(out_table) # unorganized table
        os.remove('RAxML_info.raxml')
        os.remove('RAxML_log.raxml')
        os.remove('RAxML_parsimonyTree.raxml')
        os.remove('RAxML_result.raxml')
        os.remove(directory + '.fasta.reduced')

    except FileNotFoundError:
        pass

    ### PANDA NOTES ###
    # get the index: mytable.index
    # get columns: mytable.columns
    # get a column: mytable.AF2122_NC002945_105651, shows index (sample names)
    # get a row: mytable.ix['reference'], shows columns (positions and SNPs)
    # values: mytable.values, SNPs - series
    # strip off the bottom row: mytable[:-1]
    # get the bottom row: mytable[-1:]

    # ete3 used to make svg and pdf from trees
    # Anaconda 4.0 is needed to install ete3.  Shown to work with Anaconda 4.1.6, but getcwd error occurs.  Cannot install with Anaconda 4.3
    try:
        if vdisplay_status and ete3_available:
            rooted_tree_pdf = directory + ".pdf"
            rooted_tree_svg = directory + ".svg"
            rooted_tree_path = "RAxML_bestTree.raxml.tre"
            if os.path.isfile("RAxML_bestTree.raxml.tre"):
                t = Tree(rooted_tree_path) #loads tree file
                ts = TreeStyle()
                for n in t.traverse():
                    nstyle = NodeStyle()
                    nstyle["size"] = 0 #removes dots from tree
                    n.set_style(nstyle)
                def mylayout(node):
                    if node.is_leaf():
                        nameFace = AttrFace("name", fsize=9) #sets font size of leaves
                        faces.add_face_to_node(nameFace, node, 0, position="branch-right")
                ts.layout_fn = mylayout #using custom layout above
                ts.show_leaf_name = False #using custom leaf size, so this is disabled
                ts.scale = 1000 #length of branches
                ts.branch_vertical_margin = 5 #spacing between branches
                ts.margin_left = 100
                ts.margin_right = 100
                ts.margin_top = 100
                ts.margin_bottom = 100
                t.render(rooted_tree_pdf, w=5000, tree_style=ts)
                t.render(directory + ".svg", w=500, tree_style=ts)
                os.rename(rooted_tree_path, directory + ".tre")
    except:
        pass

###############################################
###############################################
##################loopwrapper##################
###############################################
###############################################

class loop():
    
    def run_loop(self):
        home = os.path.expanduser("~")
        cpu_count = multiprocessing.cpu_count()

        startTime = datetime.now()
        print ("\n\n*** START ***\n")
        print ("Start time: %s" % startTime)

        list_of_files = glob.glob('*gz')
        list_len = len(list_of_files)
        if (list_len % 2 != 0):
            print("\n#####Check paired files.  Unpaired files seen by odd number of counted FASTQs\n\n")
            sys.exit(0)

        sample_restriction = int(cpu_count/3)

        for file in list_of_files:
            prefix_name=re.sub('_.*', '', file)
            print(prefix_name)
            if not os.path.exists(prefix_name):
                os.makedirs(prefix_name)
            shutil.move(file, prefix_name)

        ###
        #Run stats
        ts = time.time()
        st = datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')
        summary_file = root_dir+ '/stat_alignment_summary_' + st + '.xlsx'

        workbook = xlsxwriter.Workbook(summary_file)
        worksheet = workbook.add_worksheet()

        row = 0
        col = 0

        top_row_header = ["sample_name", "self.species", "reference_sequence_name", "R1size", "R2size", "allbam_mapped_reads", "genome_coverage", "ave_coverage", "ave_read_length", "unmapped_reads", "unmapped_assembled_contigs", "good_snp_count", "mlst_type", "octalcode", "sbcode", "hexadecimal_code", "binarycode"]

        for header in top_row_header:
            worksheet.write(row, col, header)
            col += 1
        ###
        #Cumulative stats
        path_found = False
        if os.path.isdir("/bioinfo11/TStuber/Results/stats"): #check bioinfo from server
            path_found = True
            copy_to = "/bioinfo11/TStuber/Results/stats"
        elif os.path.isdir("/Volumes/root/TStuber/Results"): #check bioinfo from Mac
            path_found = True
            copy_to = "/Volumes/root/TStuber/Results/stats"
        else:
            copy_to="no_path"
            print("Bioinfo not connected")

        if path_found:
            summary_cumulative_file = copy_to + '/stat_alignment_culmulative_summary' + '.xlsx'
        ###

        directory_list=[]
        for f in  os.listdir('.'):
            if not f.startswith('.'):
                directory_list.append(f)

        total_samples = len(directory_list)
        sample_restriction = int(cpu_count/4)
        lower_count = 0
        upper_count = 1
        while lower_count < total_samples:
            upper_count = lower_count + sample_restriction
            run_list = directory_list[lower_count:upper_count] #create a run list
            for i in run_list:
                directory_list.remove(i)
            total_samples = len(directory_list)
            print(run_list)

            print("Iterating directories")
            if options.debug_call: #run just one sample at a time to debug
                for d in run_list:
                    print("DEBUGGING, SAMPLES RAN INDIVIDUALLY")
                    stat_summary = read_aligner(d)
                    col = 0
                    row += 1
                    for v in stat_summary.values():
                        worksheet.write(row, col, v)
                        col += 1
                    os.chdir(root_dir)
            else: # run all in run_list in parallel
                print("SAMPLES RAN IN PARALLEL")
                with futures.ProcessPoolExecutor(max_workers=sample_restriction) as pool: #max_workers=cpu_count
                    for stat_summary in pool.map(read_aligner, run_list): #run in parallel run_list in read_aligner (script1)
                        print("statsummary")
                        print(stat_summary) #stat_summary returned from script 1
                        col = 0
                        row += 1
                        #run stats
                        for v in stat_summary.values():
                            worksheet.write(row, col, v) #stat summary to be attached in email and left in working directory
                            col += 1
                        stats_lock = False
                        if not options.quiet and path_found:
                            try: #try to open cumulative stats file
                                mytable=pd.read_excel(summary_cumulative_file)
                                top=mytable[0:0]
                                stat_summary_list = list(stat_summary.values())
                                stat_summary_list.insert(0, st)
                                while len(stat_summary_list) < 18:
                                    stat_summary_list.append("-")
                                in_dict_stats=OrderedDict(zip(top, stat_summary_list))
                                df_dict_stats=pd.DataFrame(in_dict_stats, index=[0])
                                frames = [mytable, df_dict_stats]
                                df_cum_stat = pd.concat(frames)
                                df_cum_stat.to_excel(summary_cumulative_file)
                            except: # if cannot open cumulative stats file place a copy of run stats in the stats folder
                                print("Cumulative stats file is locked")
                                stats_lock = True

        try:
            runtime = (datetime.now() - startTime)
            col = 0
            row += 1
            worksheet.write(row, col, "runtime: %s: " % runtime)
            workbook.close()
        except:
            print("ERROR CLOSING STATS FILE")
            pass

        if stats_lock: #if file was locked try to copy
            try: #will not copy if path unavailable
                shutil.copy2(summary_file, copy_to)
            except:
                pass

        ####send email:

        def send_email(email_list):
            text = "See attached:  "
            send_from = "tod.p.stuber@aphis.usda.gov"
            send_to = email_list
            msg = MIMEMultipart()
            msg['From'] = send_from
            msg['To'] = send_to
            msg['Date'] = formatdate(localtime = True)
            if not path_found:
                msg['Subject'] = "###CUMULATIVE STATS NOT UPDATED - Script1 stats summary"
            else:
                msg['Subject'] = "Script1 stats summary"
            msg.attach(MIMEText(text))

            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(summary_file, "rb").read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="summary_file.xlsx"')
            msg.attach(part)

            #context = ssl.SSLContext(ssl.PROTOCOL_SSLv3)
            #SSL connection only working on Python 3+
            smtp = smtplib.SMTP('10.10.8.12')

            smtp.send_message(msg)
            #smtp.sendmail(send_from, send_to, msg.as_string())
            smtp.quit()

        if options.email:
            send_email(email_list)


        print ("\n\nruntime: %s:  \n" % runtime)

################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
global root_dir
root_dir = str(os.getcwd())


parser = OptionParser()

#universal
parser.add_option('-s', '--species', action='store', dest='species', help='--> -s option: USE TO FORCE SPECIES TYPE <--', metavar='<OPTIONAL options: bovis, h37, ab1, ab3, suis1, mel1, mel2, mel3, canis, ceti1, ceti2, para')
parser.add_option('-d', '--debug', action='store_true', dest='debug_call', help='debug, run without loop')
parser.add_option('-m', '--email', action='store', dest='email', help='[**NVSL only**, specify own SMTP address for functionality] email recipients: all, s, tod, jess, suelee, chris, email_address')

#script 1 specific
parser.add_option('-q', '--quiet', action='store_true', dest='quiet', help='prevent stats going to cumlative collection')

#script 2 specific
parser.add_option('-a', '--all_vcf', action='store_true', dest='all_vcf', help='make tree using all VCFs')
parser.add_option('-e', '--elite', action='store_true', dest='elite', help='create a tree with on elite sample representation')
parser.add_option('-u', '--upload', action='store_true', dest='upload', help='[**NVSL only**, specify own storage for functionality] upload files to the bioinfo drive')
parser.add_option('-f', '--filter', action='store_true', dest='filter', help='Find possible positions to filter')

(options, args) = parser.parse_args()
print ("SET OPTIONS: ")
print (options)

if options.email == "all":
    email_list = "tod.p.stuber@aphis.usda.gov, Jessica.A.Hicks@aphis.usda.gov, Christine.R.Quance@aphis.usda.gov, Suelee.Robbe-Austerman@aphis.usda.gov, patrick.m.camp@aphis.usda.gov, David.T.Farrell@aphis.usda.gov, Robin.L.Swanson@aphis.usda.gov, hannah.m.tharp@aphis.usda.gov, Doris.M.Bravo@aphis.usda.gov"
elif options.email == "tod":
    email_list = "tod.p.stuber@aphis.usda.gov"
elif options.email == "jess":
    email_list = "Jessica.A.Hicks@aphis.usda.gov"
elif options.email == "suelee":
    email_list = "tod.p.stuber@aphis.usda.gov, Jessica.A.Hicks@aphis.usda.gov, Suelee.Robbe-Austerman@aphis.usda.gov"
elif options.email == "chris":
    email_list = "tod.p.stuber@aphis.usda.gov, Jessica.A.Hicks@aphis.usda.gov, Christine.R.Quance@aphis.usda.gov, Suelee.Robbe-Austerman@aphis.usda.gov"
else:
    email_list = "tod.p.stuber@aphis.usda.gov"

################################################################################################################################################


all_file_types_count = len(glob.glob('*.*'))
fastq_check = len(glob.glob('*fastq.gz'))
vcf_check = len(glob.glob('*vcf'))

if fastq_check > 0:
    fastq_check = True
if vcf_check > 0:
    vcf_check = True
if fastq_check and vcf_check:
    print("\n#####You have a mix of FASTQ and VCF files.  This is not allowed\n\n")
    sys.exit(0)

if fastq_check:
    R1 = glob.glob('*_R1*fastq.gz')
    R2 = glob.glob('*_R2*fastq.gz')
    R1count = len(R1)
    R2count = len(R2)
    fastq_count = R1count + R2count
    if (fastq_count % 2 != 0):
        print("\n#####Check paired files.  Unpaired files seen by odd number of counted FASTQs\n\n")
        sys.exit(0)
    if (R1count != R2count):
        print("\n#####Check paired files.  R1 files do not equal R2\n\n")
        sys.exit(0)
    if (all_file_types_count != fastq_count):
        print("\n#####Only zipped FASTQ files are allowed in directory\n\n")
        sys.exit(0)
    elif (fastq_count > 1):
        if options.all_vcf or options.elite or options.upload or options.filter:
            print("#####Incorrect use of options when running loop/script 1")
            sys.exit(0)
        else:
            print("--> RUNNING LOOP/SCRIPT 1") #
            loop().run_loop()
elif vcf_check:
    vcfs_count = len(glob.glob('*vcf'))
    if (all_file_types_count != vcfs_count):
        print("\n#####You have more than just VCF files in your directory.  Only VCF files are allowed if running script 2\n\n")
        sys.exit(0)
    else:
        if options.quiet:
            print("#####Incorrect use of options when running script 2")
            sys.exit(0)
        else:
            print("--> RUNNING SCRIPT 2") #
            script2().run_script2()
else:
    print ("#####Error determining file type.")
    sys.exit(0)

