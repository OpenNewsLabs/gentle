import os

from gentle import kaldi_queue
from gentle import transcription
from gentle.transcriber import MultiThreadedTranscriber
from gentle.transcription import Transcription

class FullTranscriber():

    def __init__(self, resources, nthreads=2):
        print "Flag 1: in FullTranscriber initialization"
        self.available = False
        if nthreads <= 0: return
        # TODO: Having some trouble with line below. seems to return false even with the file present.
        # if not os.path.exists(resources.full_hclg_path): return
        # print resources.full_hclg_path
        # print resources.nnet_gpu_path
        # print resources.proto_langdir
        queue = kaldi_queue.build(resources, nthreads=nthreads)
        self.mtt = MultiThreadedTranscriber(queue, nthreads=nthreads)
        self.available = True
        print "Flag 2: at end of FullTranscriber initialization"


    def transcribe(self, wavfile, progress_cb=None, logging=None):
        print "Flag 3: inside FullTranscriber transcribe method"
        words = self.mtt.transcribe(wavfile, progress_cb=progress_cb)
        print "Flag 4: inside FullTranscriber transcribe method after MultiThreadedTranscriber transcribe call"
        return self.make_transcription_alignment(words)

    @staticmethod
    def make_transcription_alignment(trans):
        # Spoof the `diff_align` output format
        transcript = ""
        words = []
        for t_wd in trans:
            word = transcription.Word(
                case="success",
                startOffset=len(transcript),
                endOffset=len(transcript) + len(t_wd.word),
                word=t_wd.word,
                alignedWord=t_wd.word,
                phones=t_wd.phones,
                start=t_wd.start,
                end=t_wd.end)
            words.append(word)

            transcript += word.word + " "

        return Transcription(words=words, transcript=transcript)
