#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division

import argparse
import os
import sys
import json
import re

from pwd import getpwuid

# import SAMADhi stuff
CMSSW_BASE = os.environ['CMSSW_BASE']
SCRAM_ARCH = os.environ['SCRAM_ARCH']
sys.path.append(os.path.join(CMSSW_BASE,'bin', SCRAM_ARCH))

# Add default ingrid storm package
sys.path.append('/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/lib/python2.7/site-packages/storm-0.20-py2.7-linux-x86_64.egg')
sys.path.append('/nfs/soft/python/python-2.7.5-sl6_amd64_gcc44/lib/python2.7/site-packages/MySQL_python-1.2.3-py2.7-linux-x86_64.egg')

from SAMADhi import DbStore, Sample

# import some lumi utils
from FWCore.PythonUtilities.LumiList import LumiList

def get_options():
    """
    Parse and return the arguments provided by the user.
    """
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-i', dest='ids', type=int, metavar='SAMADHI_SAMPLE_ID', nargs='+',
                        help='SAMADhi sample IDs')

    options = parser.parse_args()
    if (options.ids is not None and len(options.ids) < 2):
        parser.error('You must have at least 2 samples to merge')

    return options

def get_sample(id, store):
    return store.find(Sample, Sample.sample_id == id).one()

def add_merged_sample(samples, name, comment, store):

    # Retrieve the sample from the database if it already exists. Otherwise, create a new
    # sample
    update = False
    sample = store.find(Sample, Sample.name == unicode(name)).one()
    if not sample:
        sample = Sample(unicode(name), unicode(''), unicode('NTUPLES'), 0)
        store.add(sample)
    else:
        update = True
        sample.removeFiles(store)

    store.flush()

    # Set as parent dataset of the merged sample the parent dataset
    # of the first sample
    sample.source_dataset_id = samples[0].source_dataset_id

    # Reset sample content
    sample.nevents_processed = 0
    sample.nevents = 0
    sample.normalization = 1
    sample.event_weight_sum = 0
    extras_event_weight_sum = {}
    dataset_nevents = 0
    processed_lumi = LumiList()

    for i, s in enumerate(samples):
        sample.derived_samples.add(s)

        sample.nevents_processed += s.nevents_processed
        sample.nevents += s.nevents
        sample.event_weight_sum += s.event_weight_sum
        extra_sumw = s.extras_event_weight_sum
        if extra_sumw:
            extra_sumw = json.loads(extra_sumw)
            for key in extra_sumw:
                if key in extras_event_weight_sum:
                    extras_event_weight_sum[key] += extra_sumw[key]
                else:
                    extras_event_weight_sum[key] = extra_sumw[key]

        if s.processed_lumi is not None:
            sample_processed_lumi = json.loads(s.processed_lumi)
            processed_lumi = processed_lumi | LumiList(compactList=sample_processed_lumi)

        for f in s.files:
            sample.files.add(f)

        # Get info from parent datasets
        dataset_nevents += s.source_dataset.nevents

    if len(extras_event_weight_sum) > 0:
        sample.extras_event_weight_sum = unicode(json.dumps(extras_event_weight_sum))

    if len(processed_lumi.getCompactList()) > 0:
        sample.processed_lumi = unicode(json.dumps(processed_lumi.getCompactList()))

    sample.code_version = samples[0].code_version

    if sample.nevents_processed != dataset_nevents:
        sample.user_comment = unicode("Sample was not fully processed, only " + str(sample.nevents_processed) + "/" + str(dataset_nevents) + " events were processed. " + comment)
    else:
        sample.user_comment = unicode(comment)

    sample.author = unicode(getpwuid(os.stat(os.getcwd()).st_uid).pw_name)

    sample.luminosity = sample.getLuminosity()

    print("")
    print("Merged sample %s:" % ("updated" if update else "created"))
    print(sample)

    store.commit()

def main():
    options = get_options()

    print "Merging non-resonant HH samples: %s" % ', '.join(str(i) for i in options.ids)
    print("")

    dbstore = DbStore()

    print("Checking that the samples already exist in the database...")
    samples = []
    for id in options.ids:
        sample = get_sample(id, dbstore)
        if not sample:
            raise AssertionError("Aborting: the sample %d does not exist in the database, please insert it first" % id)

        samples.append(sample)
    print("All good. Continuing...")

    # Sanity check. Ensure that all parent datasets have the same cross-section
    dataset_xsec = None
    for sample in samples:
        if not dataset_xsec:
            dataset_xsec = sample.source_dataset.xsection
        else:
            if dataset_xsec != sample.source_dataset.xsection:
                raise AssertionError("Aborting: the parent datasets do not have the same cross-section. Merging would be ill-defined.")

    r = re.compile('(GluGluToHHTo2B2VTo2L2Nu_)node_.*(_13TeV-madgraph_.*)')

    # Ensure that all samples match the regex
    for sample in samples:
        if not r.match(sample.name):
            raise AssertionError("Aborting: sample %d's name (%s) does not match expected name." % (sample.sample_id, sample.name))

    merged_sample_name = r.sub(r'\g<1>all_nodes\g<2>', samples[0].name)

    print "Constructing merged sample %r ..." % merged_sample_name

    comment = 'Merging of SAMADhi samples %s' % ', '.join(str(i) for i in options.ids)

    add_merged_sample(samples, merged_sample_name, comment, dbstore)

if __name__ == '__main__':
    main()
