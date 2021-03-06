#!/usr/bin/env python3
from olctools.accessoryFunctions.accessoryFunctions import filer, make_path
from vsnp.vsnp_vcf_methods import VCFMethods
from vsnp.vsnp_vcf_run import VCF, run_cmd
from datetime import datetime
from pathlib import Path
import multiprocessing
from glob import glob
import subprocess
import pytest
import shutil
import os

__author__ = 'adamkoziol'

test_path = os.path.abspath(os.path.dirname(__file__))
file_path = os.path.join(test_path, 'files', 'fastq')
dependency_path = os.path.join(os.path.dirname(test_path), 'dependencies')
report_path = os.path.join(file_path, 'reports')
logfile = os.path.join(file_path, 'log')
threads = multiprocessing.cpu_count() - 1
home = str(Path.home())
# Define the start time
start_time = datetime.now()


def test_deepvariant_version():
    global deepvariant_version
    deepvariant_version = '0.8.0'
    cmd = 'docker run --rm gcr.io/deepvariant-docker/deepvariant:{dvv} ' \
          '/opt/deepvariant/bin/call_variants -h'.format(dvv=deepvariant_version)
    cmd_sts, return_code = run_cmd(cmd)
    if not cmd_sts:
        deepvariant_version = '0.7.2'
        cmd = 'docker run --rm gcr.io/deepvariant-docker/deepvariant:{dvv} ' \
              '/opt/deepvariant/bin/call_variants -h'.format(dvv=deepvariant_version)
        cmd_sts, return_code = run_cmd(cmd=cmd)
        if not cmd_sts:
            raise subprocess.CalledProcessError(return_code, cmd=cmd)


def test_invalid_path():
    with pytest.raises(AssertionError):
        assert VCF(path='not_a_real_path',
                   threads=threads,
                   debug=False,
                   reference_mapper='bowtie2',
                   variant_caller='freebayes',
                   matching_hashes=500)


def test_valid_path():
    vcf_object = VCF(path=file_path,
                     threads=threads,
                     debug=False,
                     reference_mapper='bowtie2',
                     variant_caller='deepvariant',
                     matching_hashes=500)
    assert vcf_object


def test_tilde_path():
    VCF(path='~',
        threads=threads,
        debug=False,
        reference_mapper='bowtie2',
        variant_caller='freebayes',
        matching_hashes=500
        )


def test_empty_filer():
    fileset = filer(filelist=list())
    assert fileset == set()


def test_empty_filer_dict():
    filedict = filer(filelist=list(),
                     returndict=True)
    assert filedict == dict()


def test_normal_filer_dict():
    filedict = filer(filelist=['03-1057_S10_L001_R1_001.fastq.gz', '03-1057_S10_L001_R2_001.fastq.gz',
                               '13-1941_S4_L001_R1_001.fastq.gz', '13-1941_S4_L001_R2_001.fastq.gz'],
                     returndict=True)
    assert [file_name for file_name in filedict] == ['03-1057', '13-1941']


def test_normal_filer():
    fileset = filer(filelist=['03-1057_S10_L001_R1_001.fastq.gz', '03-1057_S10_L001_R2_001.fastq.gz',
                              '13-1941_S4_L001_R1_001.fastq.gz', '13-1941_S4_L001_R2_001.fastq.gz'])
    assert fileset == {'03-1057', '13-1941'}


def test_missing_file_filer():
    fileset = filer(filelist=['03-1057_S10_L001_R1_001.fastq.gz', '03-1057_S10_L001_R2_001.fastq.gz',
                              '13-1941_S4_L001_R1_001.fastq.gz'])
    assert fileset == {'03-1057', '13-1941'}


def test_non_illumina_filer():
    fileset = filer(filelist=['03-1057_R1.fastq.gz', '03-1057_R2.fastq.gz',
                              '13-1941_R1.fastq.gz', '13-1941_R2.fastq.gz'])
    assert fileset == {'03-1057', '13-1941'}


def test_multiple_differences_filer():
    fileset = filer(filelist=['03-1057_1.fastq', '03-1057_2.fastq',
                              '13-1941_1.fastq.gz', '13-1941_2.fastq'])
    assert fileset == {'03-1057', '13-1941'}


def test_no_directions_filer():
    fileset = filer(filelist=['03-1057.fastq.gz', '13-1941_S4_L001.fastq'])
    assert fileset == {'03-1057', '13-1941'}


def test_vcf_file_list_no_files():
    with pytest.raises(AssertionError):
        VCFMethods.file_list(path=test_path)


def test_vcf_file_list():
    global file_list
    file_list = VCFMethods.file_list(path=file_path)
    assert len(file_list) == 7


def test_strain_dict():
    global strain_folder_dict
    strain_folder_dict = VCFMethods.strain_list(fastq_files=file_list)
    for strain_folder, fastq_files in strain_folder_dict.items():
        if '13-1941' in strain_folder:
            assert len(fastq_files) == 1
        else:
            assert len(fastq_files) == 2


def test_strain_namer_no_input():
    strain_names = VCFMethods.strain_namer(strain_folders=str())
    assert len(strain_names) == 0


def test_strain_namer_working():
    global strain_name_dict
    strain_name_dict = VCFMethods.strain_namer(strain_folders=strain_folder_dict)
    assert [strain for strain in strain_name_dict] == ['13-1941', '13-1950', 'B13-0234', 'NC_002695']


def test_make_path():
    global make_path_folder
    make_path_folder = os.path.join(test_path, 'test_folder')
    make_path(make_path_folder)
    assert os.path.isdir(make_path_folder)


def test_rm_path():
    os.rmdir(make_path_folder)
    assert os.path.isdir(make_path_folder) is False


def test_strain_linker():
    global strain_fastq_dict
    strain_fastq_dict = VCFMethods.file_link(strain_folder_dict=strain_folder_dict,
                                             strain_name_dict=strain_name_dict)
    assert [strain for strain in strain_fastq_dict] == ['13-1941', '13-1950', 'B13-0234', 'NC_002695']
    for strain_name, fastq_files in strain_fastq_dict.items():
        if strain_name == '13-1941':
            assert len(fastq_files) == 1
        else:
            assert len(fastq_files) == 2
        for symlink in fastq_files:
            assert os.path.islink(symlink)


def test_reformat_quality():
    global strain_qhist_dict, strain_lhist_dict
    strain_qhist_dict, strain_lhist_dict = VCFMethods.run_reformat_reads(strain_fastq_dict=strain_fastq_dict,
                                                                         strain_name_dict=strain_name_dict,
                                                                         logfile=logfile)
    for strain_name, qhist_paths in strain_qhist_dict.items():
        for strain_qhist_file in qhist_paths:
            assert os.path.basename(strain_qhist_file).startswith(strain_name)
            assert strain_qhist_file.endswith('_qchist.csv')


def test_parse_reformat_quality():
    global strain_average_quality_dict, strain_qual_over_thirty_dict
    strain_average_quality_dict, strain_qual_over_thirty_dict = VCFMethods. \
        parse_quality_histogram(strain_qhist_dict=strain_qhist_dict)
    assert strain_average_quality_dict['13-1950'] == [33.82559209616877, 28.64100810052621]
    assert strain_qual_over_thirty_dict['13-1950'] == [84.5724480421427, 61.085547466494404]


def test_parse_reformat_length():
    global strain_avg_read_lengths
    strain_avg_read_lengths = VCFMethods.parse_length_histograms(strain_lhist_dict=strain_lhist_dict)
    assert strain_avg_read_lengths['13-1950'] == 230.9919625


def test_file_size():
    global strain_fastq_size_dict
    strain_fastq_size_dict = VCFMethods.find_fastq_size(strain_fastq_dict)
    assert strain_fastq_size_dict['13-1950'] == [32.82019233703613, 37.25274848937988]


def test_mash_sketch():
    global fastq_sketch_dict
    fastq_sketch_dict = VCFMethods.call_mash_sketch(strain_fastq_dict=strain_fastq_dict,
                                                    strain_name_dict=strain_name_dict,
                                                    logfile=logfile)
    for strain, sketch_file in fastq_sketch_dict.items():
        assert os.path.isfile(sketch_file)


def test_mash_dist():
    global mash_dist_dict
    mash_dist_dict = VCFMethods.call_mash_dist(strain_fastq_dict=strain_fastq_dict,
                                               strain_name_dict=strain_name_dict,
                                               fastq_sketch_dict=fastq_sketch_dict,
                                               ref_sketch_file=os.path.join(
                                                   dependency_path, 'mash', 'vsnp_reference.msh'),
                                               logfile=logfile)
    for strain, tab_output in mash_dist_dict.items():
        assert os.path.isfile(tab_output)


def test_mash_accession_species():
    global accession_species_dict
    accession_species_dict = VCFMethods.parse_mash_accession_species(mash_species_file=os.path.join(
        dependency_path, 'mash', 'species_accessions.csv'))
    assert accession_species_dict['NC_002945v4.fasta'] == 'af'


def test_mash_best_ref():
    global strain_best_ref_dict, strain_ref_matches_dict, strain_species_dict
    strain_best_ref_dict, strain_ref_matches_dict, strain_species_dict = \
        VCFMethods.mash_best_ref(mash_dist_dict=mash_dist_dict,
                                 accession_species_dict=accession_species_dict,
                                 min_matches=500)
    assert strain_best_ref_dict['13-1950'] == 'NC_002945v4.fasta'
    assert strain_ref_matches_dict['13-1950'] == 916
    assert strain_species_dict['13-1950'] == 'af'


def test_reference_file_paths():
    global reference_link_path_dict, reference_link_dict
    reference_link_path_dict, reference_link_dict = VCFMethods.reference_folder(
        strain_best_ref_dict=strain_best_ref_dict,
        dependency_path=dependency_path)
    assert reference_link_path_dict['13-1950'] == 'mycobacterium/tbc/af2122/script_dependents/NC_002945v4.fasta'


def test_bwa_index():
    global bwa_mapper_index_dict, bwa_reference_abs_path_dict, bwa_reference_dep_path_dict, \
        bwa_reference_link_path_dict, bowtie2_reference_link_path_dict
    bwa_reference_link_path_dict = dict()
    bowtie2_reference_link_path_dict = dict()
    for strain_name, ref_link in reference_link_path_dict.items():
        if strain_name in ['13-1941', '13-1950']:
            bwa_reference_link_path_dict[strain_name] = ref_link
        else:
            bowtie2_reference_link_path_dict[strain_name] = ref_link
    bwa_mapper_index_dict, bwa_reference_abs_path_dict, bwa_reference_dep_path_dict = \
        VCFMethods.index_ref_genome(reference_link_path_dict=bwa_reference_link_path_dict,
                                    dependency_path=dependency_path,
                                    logfile=logfile,
                                    reference_mapper='bwa')
    assert os.path.isfile(os.path.join(dependency_path, 'mycobacterium', 'tbc', 'af2122', 'script_dependents',
                                       'NC_002945v4.fasta.bwt'))
    assert os.path.split(bwa_mapper_index_dict['13-1950'])[-1] == 'NC_002945v4.fasta'


def test_bowtie2_build():
    global bowtie2_mapper_index_dict, bowtie2_reference_abs_path_dict, bowtie2_reference_dep_path_dict
    bowtie2_mapper_index_dict, bowtie2_reference_abs_path_dict, bowtie2_reference_dep_path_dict = \
        VCFMethods.index_ref_genome(reference_link_path_dict=bowtie2_reference_link_path_dict,
                                    dependency_path=dependency_path,
                                    logfile=logfile,
                                    reference_mapper='bowtie2')
    assert os.path.isfile(os.path.join(dependency_path, 'brucella', 'suis1', 'script_dependents',
                                       'NC_017251-NC_017250.1.bt2'))
    assert os.path.split(bowtie2_mapper_index_dict['B13-0234'])[-1] == 'NC_017251-NC_017250'


def test_consolidate_index_dicts():
    global strain_mapper_index_dict, strain_reference_abs_path_dict, strain_reference_dep_path_dict
    strain_mapper_index_dict = dict()
    strain_reference_abs_path_dict = dict()
    strain_reference_dep_path_dict = dict()
    for strain_name, index_file in bwa_mapper_index_dict.items():
        strain_mapper_index_dict[strain_name] = index_file
        strain_reference_abs_path_dict[strain_name] = bwa_reference_abs_path_dict[strain_name]
        strain_reference_dep_path_dict[strain_name] = bwa_reference_dep_path_dict[strain_name]
    for strain_name, index_file in bowtie2_mapper_index_dict.items():
        strain_mapper_index_dict[strain_name] = index_file
        strain_reference_abs_path_dict[strain_name] = bowtie2_reference_abs_path_dict[strain_name]
        strain_reference_dep_path_dict[strain_name] = bowtie2_reference_dep_path_dict[strain_name]
    assert os.path.split(strain_mapper_index_dict['13-1950'])[-1] == 'NC_002945v4.fasta'
    assert os.path.split(strain_mapper_index_dict['B13-0234'])[-1] == 'NC_017251-NC_017250'


def test_bwa_mem():
    global bwa_sorted_bam_dict
    # Create a dictionary of the subset of strains to process with bwa
    bwa_strain_fastq_dict = dict()
    for strain_name, fastq_files in strain_fastq_dict.items():
        if strain_name in ['13-1941', '13-1950']:
            bwa_strain_fastq_dict[strain_name] = fastq_files
    bwa_sorted_bam_dict = VCFMethods.map_ref_genome(strain_fastq_dict=bwa_strain_fastq_dict,
                                                    strain_name_dict=strain_name_dict,
                                                    strain_mapper_index_dict=strain_mapper_index_dict,
                                                    threads=threads,
                                                    logfile=logfile,
                                                    reference_mapper='bwa')
    for strain_name, sorted_bam in bwa_sorted_bam_dict.items():
        assert os.path.isfile(sorted_bam)


def test_bowtie2_map():
    global bowtie2_sorted_bam_dict
    # Create a dictionary of the subset of strains to process with bowtie2
    bowtie2_strain_fastq_dict = dict()
    for strain_name, fastq_files in strain_fastq_dict.items():
        if strain_name in ['B13-0234', 'NC_002695']:
            bowtie2_strain_fastq_dict[strain_name] = fastq_files
    bowtie2_sorted_bam_dict = VCFMethods.map_ref_genome(strain_fastq_dict=bowtie2_strain_fastq_dict,
                                                        strain_name_dict=strain_name_dict,
                                                        strain_mapper_index_dict=strain_mapper_index_dict,
                                                        threads=threads,
                                                        logfile=logfile,
                                                        reference_mapper='bowtie2')
    for strain_name, sorted_bam in bowtie2_sorted_bam_dict.items():
        assert os.path.isfile(sorted_bam)


def test_merge_bwa_bowtie_bam_dict():
    global strain_sorted_bam_dict
    strain_sorted_bam_dict = dict()
    for strain_name, sorted_bam in bwa_sorted_bam_dict.items():
        strain_sorted_bam_dict[strain_name] = sorted_bam
    for strain_name, sorted_bam in bowtie2_sorted_bam_dict.items():
        strain_sorted_bam_dict[strain_name] = sorted_bam
    assert strain_sorted_bam_dict['13-1950']
    assert strain_sorted_bam_dict['B13-0234']


def test_unmapped_reads_extract():
    global strain_unmapped_reads_dict
    strain_unmapped_reads_dict = VCFMethods.extract_unmapped_reads(strain_sorted_bam_dict=strain_sorted_bam_dict,
                                                                   strain_name_dict=strain_name_dict,
                                                                   threads=threads,
                                                                   logfile=logfile)
    for strain_name, unmapped_reads_fastq in strain_unmapped_reads_dict.items():
        assert os.path.getsize(unmapped_reads_fastq) > 0


def test_skesa_assembled_unmapped():
    global strain_skesa_output_fasta_dict
    strain_skesa_output_fasta_dict = VCFMethods.assemble_unmapped_reads(
        strain_unmapped_reads_dict=strain_unmapped_reads_dict,
        strain_name_dict=strain_name_dict,
        threads=threads,
        logfile=logfile)
    assert os.path.getsize(strain_skesa_output_fasta_dict['B13-0234']) == 0


def test_number_unmapped_contigs():
    global strain_unmapped_contigs_dict
    strain_unmapped_contigs_dict = VCFMethods.assembly_stats(
        strain_skesa_output_fasta_dict=strain_skesa_output_fasta_dict)
    assert strain_unmapped_contigs_dict['B13-0234'] == 0


def test_samtools_index():
    VCFMethods.samtools_index(strain_sorted_bam_dict=strain_sorted_bam_dict,
                              strain_name_dict=strain_name_dict,
                              threads=threads,
                              logfile=logfile)
    for strain_name, sorted_bam in strain_sorted_bam_dict.items():
        assert os.path.isfile(sorted_bam + '.bai')


def test_qualimap():
    global strain_qualimap_report_dict
    strain_qualimap_report_dict = VCFMethods.run_qualimap(strain_sorted_bam_dict=strain_sorted_bam_dict,
                                                          strain_name_dict=strain_name_dict,
                                                          logfile=logfile)
    for strain_name, qualimap_report in strain_qualimap_report_dict.items():
        assert os.path.isfile(qualimap_report)


def test_qualimap_parse():
    global strain_qualimap_outputs_dict
    strain_qualimap_outputs_dict = VCFMethods.parse_qualimap(strain_qualimap_report_dict=strain_qualimap_report_dict)
    assert int(strain_qualimap_outputs_dict['13-1950']['MappedReads'].split('(')[0]) >= 370000


def test_deepvariant_make_examples():
    global strain_examples_dict, strain_variant_path_dict, strain_gvcf_tfrecords_dict, vcf_path
    vcf_path = os.path.join(file_path, 'vcf_files')
    reduced_strain_sorted_bam_dict = dict()
    reduced_strain_sorted_bam_dict['13-1941'] = strain_sorted_bam_dict['13-1941']
    strain_examples_dict, strain_variant_path_dict, strain_gvcf_tfrecords_dict = \
        VCFMethods.deepvariant_make_examples(strain_sorted_bam_dict=reduced_strain_sorted_bam_dict,
                                             strain_name_dict=strain_name_dict,
                                             strain_reference_abs_path_dict=strain_reference_abs_path_dict,
                                             vcf_path=vcf_path,
                                             home=home,
                                             threads=threads,
                                             deepvariant_version=deepvariant_version,
                                             logfile=logfile)
    assert len(strain_examples_dict['13-1941']) == threads
    for strain_name, gvcf_tfrecord in strain_gvcf_tfrecords_dict.items():
        gvcf_tfrecord = gvcf_tfrecord.split('@')[0]
        if strain_name != 'NC_002695':
            assert len(glob('{gvcf_tfrecord}*.gz'.format(gvcf_tfrecord=gvcf_tfrecord))) == threads
        else:
            assert len(glob('{gvcf_tfrecord}*.gz'.format(gvcf_tfrecord=gvcf_tfrecord))) == 0


def test_deepvariant_call_variants():
    global strain_call_variants_dict
    strain_call_variants_dict = \
        VCFMethods.deepvariant_call_variants(strain_variant_path_dict=strain_variant_path_dict,
                                             strain_name_dict=strain_name_dict,
                                             dependency_path=dependency_path,
                                             home=home,
                                             vcf_path=vcf_path,
                                             threads=threads,
                                             logfile=logfile,
                                             variant_caller='deepvariant',
                                             deepvariant_version=deepvariant_version)
    assert os.path.getsize(strain_call_variants_dict['13-1941']) > 100
    with pytest.raises(KeyError):
        assert strain_call_variants_dict['NC_002695']


def test_deepvariant_postprocess_variants():
    global strain_vcf_dict
    strain_vcf_dict = \
        VCFMethods.deepvariant_postprocess_variants_multiprocessing(
            strain_call_variants_dict=strain_call_variants_dict,
            strain_variant_path_dict=strain_variant_path_dict,
            strain_name_dict=strain_name_dict,
            strain_reference_abs_path_dict=strain_reference_abs_path_dict,
            strain_gvcf_tfrecords_dict=strain_gvcf_tfrecords_dict,
            vcf_path=vcf_path,
            home=home,
            logfile=logfile,
            deepvariant_version=deepvariant_version,
            threads=threads)
    assert os.path.getsize(strain_vcf_dict['13-1941']) > 100
    with pytest.raises(KeyError):
        assert strain_vcf_dict['NC_002695']


def test_regions():
    global strain_ref_regions_dict
    strain_ref_regions_dict = VCFMethods.reference_regions(
        strain_reference_abs_path_dict=strain_reference_abs_path_dict,
        logfile=logfile)
    for strain_name, ref_regions_file in strain_ref_regions_dict.items():
        assert os.path.isfile(ref_regions_file)
        assert os.path.getsize(ref_regions_file) > 0


def test_freebayes():
    """
    Run FreeBayes on a single strain
    """
    global strain_vcf_dict
    reduced_strain_sorted_bam_dict = dict()
    reduced_strain_sorted_bam_dict['13-1950'] = strain_sorted_bam_dict['13-1950']
    strain_vcf_dict = VCFMethods.freebayes(strain_sorted_bam_dict=reduced_strain_sorted_bam_dict,
                                           strain_name_dict=strain_name_dict,
                                           strain_reference_abs_path_dict=strain_reference_abs_path_dict,
                                           strain_ref_regions_dict=strain_ref_regions_dict,
                                           threads=threads,
                                           logfile=logfile)
    for strain_name, vcf_file in strain_vcf_dict.items():
        assert os.path.getsize(vcf_file) > 10000


def test_parse_vcf():
    global vcf_num_high_quality_snps_dict
    vcf_strain_vcf_dict = dict()
    for strain_name, vcf_file in strain_vcf_dict.items():
        if strain_name == '13-1950':
            vcf_strain_vcf_dict[strain_name] = vcf_file
    vcf_num_high_quality_snps_dict = VCFMethods.parse_vcf(strain_vcf_dict=vcf_strain_vcf_dict)
    assert vcf_num_high_quality_snps_dict['13-1950'] == 480


def test_copy_test_vcf_files():
    """
    Copy VCF files from test folder to supplement the lone deepvariant-created VCF file. Populate the strain_vcf_dict
    dictionary with these VCF files
    """
    # Set the absolute path of the test folder containing the VCF files
    vcf_test_path = os.path.join(test_path, 'files', 'vcf')
    # Create a list of all the VCF files
    vcf_files = glob(os.path.join(vcf_test_path, '*.gvcf.gz'))
    for strain_name, strain_folder in strain_name_dict.items():
        if strain_name not in strain_vcf_dict:
            # Set the name of the output .vcf file
            vcf_base_name = '{sn}.gvcf.gz'.format(sn=strain_name)
            out_vcf = os.path.join(strain_folder, vcf_base_name)
            # Don't try to copy the file if the original exists
            for vcf_file in vcf_files:
                if os.path.basename(vcf_file) == vcf_base_name:
                    shutil.copyfile(vcf_file, out_vcf)
            # Update the dictionary
            strain_vcf_dict[strain_name] = out_vcf
            if strain_name != 'NC_002695':
                assert os.path.isfile(out_vcf)


def test_parse_gvcf():
    global gvcf_num_high_quality_snps_dict
    gvcf_strain_vcf_dict = dict()
    for strain_name, vcf_file in strain_vcf_dict.items():
        if strain_name != '13-1950':
            gvcf_strain_vcf_dict[strain_name] = vcf_file
    gvcf_num_high_quality_snps_dict = VCFMethods.parse_gvcf(strain_vcf_dict=gvcf_strain_vcf_dict)
    assert gvcf_num_high_quality_snps_dict['13-1941'] == 477
    assert gvcf_num_high_quality_snps_dict['B13-0234'] == 69
    assert gvcf_num_high_quality_snps_dict['NC_002695'] == 0


def test_copy_vcf_files():
    VCFMethods.copy_vcf_files(strain_vcf_dict=strain_vcf_dict,
                              vcf_path=vcf_path)
    assert os.path.isdir(vcf_path)
    assert len(glob(os.path.join(vcf_path, '*.gvcf.gz'))) == 2
    assert len(glob(os.path.join(vcf_path, '*.gvcf'))) == 1


def test_consolidate_high_quality_snp_dicts():
    global strain_num_high_quality_snps_dict
    strain_num_high_quality_snps_dict = dict()
    for strain_name, num_high_quality_snps in gvcf_num_high_quality_snps_dict.items():
        strain_num_high_quality_snps_dict[strain_name] = num_high_quality_snps
    for strain_name, num_high_quality_snps in vcf_num_high_quality_snps_dict.items():
        strain_num_high_quality_snps_dict[strain_name] = num_high_quality_snps
    assert strain_num_high_quality_snps_dict['13-1941'] == 477
    assert strain_num_high_quality_snps_dict['B13-0234'] == 69
    assert strain_num_high_quality_snps_dict['NC_002695'] == 0
    assert strain_num_high_quality_snps_dict['13-1950'] == 480


def test_spoligo_bait():
    global strain_spoligo_stats_dict
    strain_spoligo_stats_dict = VCFMethods.bait_spoligo(strain_fastq_dict=strain_fastq_dict,
                                                        strain_name_dict=strain_name_dict,
                                                        spoligo_file=os.path.join(dependency_path,
                                                                                  'mycobacterium',
                                                                                  'spacers.fasta'),
                                                        threads=threads,
                                                        logfile=logfile,
                                                        kmer=25)
    for strain_name, spoligo_stats_file in strain_spoligo_stats_dict.items():
        assert os.path.getsize(spoligo_stats_file) > 0


def test_spoligo_parse():
    global strain_binary_code_dict, strain_octal_code_dict, strain_hexadecimal_code_dict
    strain_binary_code_dict, \
        strain_octal_code_dict, \
        strain_hexadecimal_code_dict = \
        VCFMethods.parse_spoligo(strain_spoligo_stats_dict=strain_spoligo_stats_dict)
    assert strain_binary_code_dict['13-1950'] == '1101000000000010111111111111111111111100000'
    assert strain_octal_code_dict['13-1950'] == '640013777777600'
    assert strain_hexadecimal_code_dict['13-1950'] == '68-0-5F-7F-FF-60'


def test_extract_sbcode():
    global strain_sbcode_dict
    strain_sbcode_dict = VCFMethods.extract_sbcode(strain_reference_dep_path_dict=strain_reference_dep_path_dict,
                                                   strain_octal_code_dict=strain_octal_code_dict)
    assert strain_sbcode_dict['13-1950'] == 'SB0145'


def test_brucella_mlst():
    global mlst_report
    VCFMethods.brucella_mlst(seqpath=file_path,
                             mlst_db_path=os.path.join(dependency_path, 'brucella', 'MLST'),
                             logfile=logfile)
    mlst_report = os.path.join(file_path, 'reports', 'mlst.csv')
    assert os.path.getsize(mlst_report) > 100


def test_mlst_parse():
    global strain_mlst_dict
    strain_mlst_dict = VCFMethods.parse_mlst_report(strain_name_dict=strain_name_dict,
                                                    mlst_report=mlst_report)
    assert strain_mlst_dict['13-1950']['sequence_type'] == 'ND'
    assert strain_mlst_dict['13-1950']['matches'] == 'ND'
    assert strain_mlst_dict['B13-0234']['sequence_type'] == '14'
    assert strain_mlst_dict['B13-0234']['matches'] == '9'


def test_report_create():
    global vcf_report
    vcf_report = VCFMethods.create_vcf_report(
        start_time=start_time,
        strain_species_dict=strain_species_dict,
        strain_best_ref_dict=strain_best_ref_dict,
        strain_fastq_size_dict=strain_fastq_size_dict,
        strain_average_quality_dict=strain_average_quality_dict,
        strain_qual_over_thirty_dict=strain_qual_over_thirty_dict,
        strain_qualimap_outputs_dict=strain_qualimap_outputs_dict,
        strain_avg_read_lengths=strain_avg_read_lengths,
        strain_unmapped_contigs_dict=strain_unmapped_contigs_dict,
        strain_num_high_quality_snps_dict=strain_num_high_quality_snps_dict,
        strain_mlst_dict=strain_mlst_dict,
        strain_octal_code_dict=strain_octal_code_dict,
        strain_sbcode_dict=strain_sbcode_dict,
        strain_hexadecimal_code_dict=strain_hexadecimal_code_dict,
        strain_binary_code_dict=strain_binary_code_dict,
        report_path=report_path)
    assert os.path.getsize(vcf_report) > 100


def test_remove_bt2_indexes():
    for strain_name, ref_link in reference_link_path_dict.items():
        # Set the absolute path, and strip off the file extension for use in the build call
        ref_abs_path = os.path.dirname(os.path.abspath(os.path.join(dependency_path, ref_link)))
        bt2_files = glob(os.path.join(ref_abs_path, '*.bt2'))
        for bt2_index in bt2_files:
            os.remove(bt2_index)
        bt2_files = glob(os.path.join(ref_abs_path, '*.bt2'))
        assert not bt2_files


def test_remove_bwa_indexes():
    for strain_name, ref_link in reference_link_path_dict.items():
        ref_abs_path = os.path.dirname(os.path.abspath(os.path.join(dependency_path, ref_link)))
        for ref_file in glob(os.path.join(ref_abs_path, '*')):
            for extension in ['.bwt', '.pac', '.sa', '.amb', '.ann']:
                if ref_file.endswith(extension):
                    os.remove(ref_file)


def test_remove_logs():
    logs = glob(os.path.join(file_path, '*.txt'))
    for log in logs:
        os.remove(log)


def test_remove_mlst_logs():
    logs = glob(os.path.join(dependency_path, 'brucella', 'MLST', '*.log'))
    for log in logs:
        os.remove(log)


def test_remove_reports():
    shutil.rmtree(report_path)


def test_remove_vcf_path():
    shutil.rmtree(vcf_path)


def test_remove_working_dir():
    for strain_name, working_dir in strain_name_dict.items():
        shutil.rmtree(working_dir)
