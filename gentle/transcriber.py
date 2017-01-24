import math
import logging
import wave

from gentle import transcription

from multiprocessing.pool import ThreadPool as Pool

class MultiThreadedTranscriber:
    def __init__(self, kaldi_queue, chunk_len=20, overlap_t=2, nthreads=4):
        print "Flag: in MultiThreadedTranscriber initialization "
        self.chunk_len = chunk_len
        self.overlap_t = overlap_t
        self.nthreads = nthreads
        self.kaldi_queue = kaldi_queue
        # print self.chunk_len
        # print self.overlap_t 
        # print self.nthreads
        # print self.kaldi_queue
        print "Flag: end of MultiThreadedTranscriber initialization "

    def transcribe(self, wavfile, progress_cb=None):
        print "Flag 3.1: in MultiThreadedTranscriber transcribe function"
        wav_obj = wave.open(wavfile, 'r')
        duration = wav_obj.getnframes() / float(wav_obj.getframerate())
        n_chunks = int(math.ceil(duration / float(self.chunk_len - self.overlap_t)))

        chunks = []
        print "Flag 3.2: in MultiThreadedTranscriber transcribe function - after def chunks"
        def transcribe_chunk(idx):
            print "Flag 3.4.1: in transcribe_chunk"
            wav_obj = wave.open(wavfile, 'r')
            start_t = idx * (self.chunk_len - self.overlap_t)

            # Seek
            wav_obj.setpos(int(start_t * wav_obj.getframerate()))
            print "Flag 3.4...: in of transcribe_chunk"
            # Read frames
            buf = wav_obj.readframes(int(self.chunk_len * wav_obj.getframerate()))

            k = self.kaldi_queue.get()    
            print k     
            k.push_chunk(buf)
            print "FLAGGGGG"
            ret = k.get_final()
            k.reset()
            self.kaldi_queue.put(k)
            chunks.append({"start": start_t, "words": ret})
            logging.info('%d/%d' % (len(chunks), n_chunks))
            print "Flag 3.4...: before if end of transcribe_chunk"
            if progress_cb is not None:
                progress_cb({"message": ' '.join([X['word'] for X in ret]),
                             "percent": len(chunks) / float(n_chunks)})

        print "Flag 3.3: in MultiThreadedTranscriber transcribe function - after def transcribe_chunk"
        # TODO: this is causing an issue!
        # print n_chunks
        # print self.nthreads
        pool = Pool(min(n_chunks, self.nthreads))
        print "Flag 3.4"
        # print type(transcribe_chunk)
        print n_chunks
        print range(n_chunks)
        pool.map(transcribe_chunk, range(n_chunks))

        print "Flag 3.5"
        pool.close()
        print "Flag 3.6"
        chunks.sort(key=lambda x: x['start'])

        # Combine chunks
        words = []
        for c in chunks:
            chunk_start = c['start']
            chunk_end = chunk_start + self.chunk_len

            chunk_words = [transcription.Word(**wd).shift(time=chunk_start) for wd in c['words']]

            # At chunk boundary cut points the audio often contains part of a
            # word, which can get erroneously identified as one or more different
            # in-vocabulary words.  So discard one or more words near the cut points
            # (they'll be covered by the ovlerap anyway).
            #
            trim = min(0.25 * self.overlap_t, 0.5)
            if c is not chunks[0]:
                while len(chunk_words) > 1:
                    chunk_words.pop(0)
                    if chunk_words[0].end > chunk_start + trim:
                        break
            if c is not chunks[-1]:
                while len(chunk_words) > 1:
                    chunk_words.pop()
                    if chunk_words[-1].start < chunk_end - trim:
                        break

            words.extend(chunk_words)

        # Remove overlap:  Sort by time, then filter out any Word entries in
        # the list that are adjacent to another entry corresponding to the same
        # word in the audio.
        words.sort(key=lambda word: word.start)
        words.append(transcription.Word(word="__dummy__"))
        words = [words[i] for i in range(len(words)-1) if not words[i].corresponds(words[i+1])]
        print "Flag 3..: in MultiThreadedTranscriber transcribe function - before returning words"
        return words


if __name__=='__main__':
    # full transcription
    from Queue import Queue
    from util import ffmpeg
    from gentle import standard_kaldi

    import sys

    import logging
    logging.getLogger().setLevel('INFO')
    
    k_queue = Queue()
    for i in range(3):
        k_queue.put(standard_kaldi.Kaldi())

    trans = MultiThreadedTranscriber(k_queue)

    with gentle.resampled(sys.argv[1]) as filename:
        out = trans.transcribe(filename)

    open(sys.argv[2], 'w').write(out.to_json())

