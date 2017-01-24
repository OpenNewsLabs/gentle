'''
Trying to make a transcriber that can be run from comand line with python using Gentle.

Ideal it should. 
- align if text argument is provided
- transcribe if no text argument is provided 
- have an optional argument to pass in ffmpeg binary location, use default if not provided
- ideally also if audio already met specs does not convert it again?

but for now just looking to get a full transcription going.

Author: Pietro Passarelli - pietro.passarelli@gmail.com - @pietropassarell 
'''

import argparse
import logging
import multiprocessing
import os
import sys

import gentle



'''
Set up command line arguments parsing
'''

parser = argparse.ArgumentParser(
        description='Transcibe an audio wav file using Kaldi.  Outputs JSON')

# by defaults nthreads reads on the cpus are on the system to assign the thread number 
parser.add_argument(
        '--nthreads', default=multiprocessing.cpu_count(), metavar='nthreads', type=int,
        help='number of alignment threads')

parser.add_argument(
        '-o', '--output', metavar='output', type=str, 
        help='output filename')

parser.add_argument(
        '--conservative', dest='conservative', action='store_true',
        help='conservative alignment')
parser.set_defaults(conservative=False)

parser.add_argument(
        '--disfluency', dest='disfluency', action='store_true',
        help='include disfluencies (uh, um) in alignment')
parser.set_defaults(disfluency=False)

parser.add_argument(
        '--log', default="INFO",
        help='the log level (DEBUG, INFO, WARNING, ERROR, or CRITICAL)')

parser.add_argument(
        'audiofile', type=str,
        help='audio file, required')

parser.add_argument(
        '-t','--txtfile',metavar='txtfile', type=str,
        help='transcript text file, optional, if provided it aligns text, if not provided it transcribes')
parser.set_defaults(txtfile=None)

args = parser.parse_args()
log_level = args.log.upper()

print args.audiofile

'''
Setting up log library https://docs.python.org/2/library/logging.html 
'''
logging.getLogger().setLevel(log_level)

''''
Here it could resample the audio file to meet wav specs.
For now skipping this step and expecting as input to transcribe a wav file that meets that specifications in  `resample.py`
See example folder for compliant wav file
'''
wavfile = args.audiofile

'''
Transcribing 
- Initialise FullTranscriber 
- transcribe 
'''

def on_progress(p):
	for k,v in p.items():
		status[k] = v

resources = gentle.Resources()

ntranscriptionthreads  = args.nthreads
full_transcriber = gentle.FullTranscriber(resources, nthreads=ntranscriptionthreads)
# result = full_transcriber.transcribe(wavfile, progress_cb=on_progress, logging=logging)
if full_transcriber.available:
	full_transcriber.transcribe(wavfile, progress_cb=on_progress, logging=logging)

'''
Here could have logic for transcribijng or aligning if -t field is != None.
'''


'''
Outputing to file if -o output provided 
'''

# print result 
# fh = open(args.output, 'w') if args.output else sys.stdout
# fh.write(result.to_json(indent=2))
# if args.output:
#     logging.info("output written to %s" % (args.output))


