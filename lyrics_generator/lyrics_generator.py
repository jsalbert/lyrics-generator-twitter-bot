import os
import re
import json
import numpy as np
import tensorflow as tf


from datetime import datetime
from lyrics_generator.gpt_2 import model, sample, encoder
from tensorflow.core.protobuf import rewriter_config_pb2
from lyrics_generator.utils import process_lyrics, print_text_in_image, is_valid_prefix, \
    generate_random_parametres, mkdir, pick_random_font


class LyricsGenerator:
    def __init__(self, gpt_2_model_directory):
        self.gpt2_model = GPT2(gpt_2_model_directory)

    def generate_lyrics(self, prefix, length=256, temperature=0.8, top_k=30, top_p=0.0, random_parametres=False):
        """

        Args:
            prefix: Input text
            length: Character length of the generated output
            temperature: GPT-2 temperature parameter
            top_k: GPT-2 top_k parameter
            top_p: GPT-2 top_p parameter
            random_parametres: If True will use random parameters to generate the GPT-2 output

        Returns:n

        """
        if not is_valid_prefix(prefix):
            raise ValueError('Incorrect characters in string, only letters, numbers and [, . ? !] are supported')

        if random_parametres:
            length, temperature, top_k = generate_random_parametres()

        lyrics = self.gpt2_model.generate(
            return_as_list=True,
            prefix=prefix,
            length=length,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
        )

        # Will limit the max amount of characters per sentence to 70
        lyrics = process_lyrics(lyrics, 70)
        return lyrics

    @staticmethod
    def create_default_filepath(lyrics, mode='image'):
        song_root_path = 'files/songs/'
        timestamp = datetime.timestamp(datetime.now())
        # Folder name is first sentence of lyric + timestamp
        clip_char = min(len(lyrics[0]), 15)
        folder_name = ''.join(lyrics[0][:clip_char]).replace('\n', '').replace(' ', '_') + '_' + str(round(timestamp))

        if mode == 'image':
            return os.path.join(song_root_path, folder_name, 'song.png')
        elif mode == 'text':
            return os.path.join(song_root_path, folder_name, 'song.txt')
        else:
            return os.path.join(song_root_path, folder_name)

    def save_lyrics_app_default(self, lyrics, max_lines=25, font_path=None, image_color=(255, 255, 255)):
        filepath = self.create_default_filepath(lyrics, mode='default')
        self.save_lyrics_as_text(lyrics, os.path.join(filepath, 'song.txt'))
        image_paths = self.save_lyrics_as_images(lyrics, os.path.join(filepath, 'song.png'), max_lines=max_lines,
                                                 font_path=font_path, image_color=image_color)
        return image_paths

    def save_lyrics_as_images(self, lyrics, filepath=None, max_lines=25, font_path=None, image_color=(255, 255, 255)):
        if filepath is None:
            filepath = self.create_default_filepath(lyrics, mode='image')

        if font_path is None:
            font_path = pick_random_font()

        image_paths = []

        if len(lyrics) > max_lines:
            lyrics_chunks = [lyrics[i:i + max_lines] for i in range(0, len(lyrics), max_lines)]
            for i, lyric in enumerate(lyrics_chunks):
                filepath_list = filepath.split('.')
                filepath_i = ''.join(filepath_list[:-1]) + '_' + str(i) + '.' + filepath_list[-1]
                self.save_lyrics_as_image(lyric, filepath_i, font_path, image_color=image_color)
                image_paths.append(filepath_i)
        else:
            self.save_lyrics_as_image(lyrics, filepath, font_path, image_color=image_color)
            image_paths.append(filepath)
        return image_paths

    @staticmethod
    def save_lyrics_as_image(lyrics, filepath=None, font_path=None, image_color=(255, 255, 255)):
        if filepath is None:
            filepath = self.create_default_filepath(lyrics, mode='image')

        if not filepath.endswith(('.jpg', '.png', '.jpeg')):
            raise ValueError('Filepath must end with a valid image format')

        # Create folder
        mkdir('/'.join(filepath.split('/')[:-1]))
        if font_path is None:
            font_path = pick_random_font()

        image = print_text_in_image(lyrics, font_path, image_color=image_color)
        image.save(filepath)
        return filepath

    def save_lyrics_as_text(self, lyrics, filepath=None):
        if filepath is None:
            filepath = self.create_default_filepath(lyrics, mode='text')
        # Create folder
        mkdir('/'.join(filepath.split('/')[:-1]))
        with open(filepath, 'w') as f:
            f.write(''.join(lyrics))


class GPT2:
    def __init__(self, gpt_2_model_directory):
        self.model_dir = gpt_2_model_directory
        self.sess = self.start_tf_sess()
        self.load_gpt2()

    # Code adapted from https://github.com/minimaxir/gpt-2-simple
    @staticmethod
    def start_tf_sess(threads=-1, server=None):
        """
        Returns a tf.Session w/ config
        """
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        config.graph_options.rewrite_options.layout_optimizer = rewriter_config_pb2.RewriterConfig.OFF
        if threads > 0:
            config.intra_op_parallelism_threads = threads
            config.inter_op_parallelism_threads = threads

        if server is not None:
            return tf.Session(target=server.target, config=config)

        return tf.Session(config=config)

    def load_gpt2(self):
        """
        Loads the model checkpoint into a TensorFlow session
        for repeated predictions.
        """
        hparams = model.default_hparams()
        with open(os.path.join(self.model_dir, 'hparams.json')) as f:
            hparams.override_from_dict(json.load(f))

        context = tf.placeholder(tf.int32, [1, None])
        output = model.model(hparams=hparams, X=context)

        ckpt = tf.train.latest_checkpoint(self.model_dir)
        saver = tf.train.Saver(allow_empty=True)
        self.sess.run(tf.global_variables_initializer())

        print('Loading checkpoint', ckpt)
        saver.restore(self.sess, ckpt)

    def generate(self,
                 return_as_list=False,
                 truncate=None,
                 destination_path=None,
                 sample_delim='=' * 20 + '\n',
                 prefix=None,
                 seed=None,
                 nsamples=1,
                 batch_size=1,
                 length=1023,
                 temperature=0.7,
                 top_k=0,
                 top_p=0.0,
                 include_prefix=True):
        """
        Generates text from a model loaded into memory.

        Adapted from https://github.com/openai/gpt-2/blob/master/src/interactive_conditional_samples.py
        """

        if batch_size is None:
            batch_size = 1
        assert nsamples % batch_size == 0

        if nsamples == 1:
            sample_delim = ''

        if prefix == '':
            prefix = None

        enc = encoder.get_encoder(self.model_dir)
        hparams = model.default_hparams()

        with open(os.path.join(self.model_dir, 'hparams.json')) as f:
            hparams.override_from_dict(json.load(f))

        if prefix:
            context = tf.placeholder(tf.int32, [batch_size, None])
            context_tokens = enc.encode(prefix)

        np.random.seed(seed)
        tf.set_random_seed(seed)

        output = sample.sample_sequence(
            hparams=hparams,
            length=min(length, 1023 - (len(context_tokens) if prefix else 0)),
            start_token=enc.encoder['<|endoftext|>'] if not prefix else None,
            context=context if prefix else None,
            batch_size=batch_size,
            temperature=temperature, top_k=top_k, top_p=top_p
        )[:, 1:]

        if destination_path:
            f = open(destination_path, 'w')
        generated = 0
        gen_texts = []
        while generated < nsamples:
            if not prefix:
                out = self.sess.run(output)
            else:
                out = self.sess.run(output, feed_dict={
                    context: batch_size * [context_tokens]
                })
            for i in range(batch_size):
                generated += 1
                gen_text = enc.decode(out[i])
                if prefix:
                    gen_text = enc.decode(context_tokens[:1]) + gen_text
                if truncate:
                    truncate_esc = re.escape(truncate)
                    if prefix and not include_prefix:
                        prefix_esc = re.escape(prefix)
                        pattern = '(?:{})(.*?)(?:{})'.format(prefix_esc,
                                                             truncate_esc)
                    else:
                        pattern = '(.*?)(?:{})'.format(truncate_esc)

                    trunc_text = re.search(pattern, gen_text, re.S)
                    if trunc_text:
                        gen_text = trunc_text.group(1)
                gen_text = gen_text.lstrip('\n')
                if destination_path:
                    f.write("{}\n{}".format(gen_text, sample_delim))
                if not return_as_list and not destination_path:
                    print("{}\n{}".format(gen_text, sample_delim), end='')
                gen_texts.append(gen_text)

        if destination_path:
            f.close()

        if return_as_list:
            return gen_texts
