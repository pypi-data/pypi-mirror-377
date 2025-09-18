"""Classes for GMM alignment"""
from __future__ import annotations

import logging
import pathlib
import sys
import traceback
import typing

from _kalpy.fstext import VectorFst
from _kalpy.gmm import gmm_align_compiled, gmm_align_reference_phones
from _kalpy.matrix import FloatMatrix
from _kalpy.util import (
    BaseFloatVectorWriter,
    Int32VectorWriter,
    RandomAccessInt32VectorVectorReader,
)
from kalpy.decoder.data import FstArchive
from kalpy.feat.data import FeatureArchive
from kalpy.gmm.data import Alignment
from kalpy.gmm.utils import read_gmm_model
from kalpy.utils import generate_write_specifier

logger = logging.getLogger("kalpy.align")
logger.setLevel(logging.DEBUG)
logger.write = lambda msg: logger.info(msg) if msg != "\n" else None
logger.flush = lambda: None


class GmmAligner:
    """
    Wrapper class around aligning with a GMM acoustic model

    Parameters
    ----------
    acoustic_model_path: str or :class:`~pathlib.Path`
        Path to acoustic model
    beam: int
        Size of the beam to use in decoding, defaults to 10
    retry_beam : int
        Size of the beam to use in decoding if it fails with the initial beam width, defaults to 40
    transition_scale : float
        Transition scale, defaults to 1.0
    acoustic_scale : float
        Acoustic scale, defaults to 0.1
    self_loop_scale : float
        Self-loop scale, defaults to 0.1
    careful : bool
        Flag for extra error checking on reaching final state, defaults to False
    disambiguation_symbols : list[int], optional
        List of symbols in phone table that correspond to disambiguation symbols
    """

    def __init__(
        self,
        acoustic_model_path: typing.Union[pathlib.Path, str],
        acoustic_scale: float = 1.0,
        transition_scale: float = 1.0,
        self_loop_scale: float = 1.0,
        beam: int = 10,
        retry_beam: int = 40,
        careful: bool = False,
        disambiguation_symbols: typing.List[int] = None,
    ):
        self.acoustic_model_path = str(acoustic_model_path)
        self.transition_model, self.acoustic_model = read_gmm_model(self.acoustic_model_path)
        self.acoustic_scale = acoustic_scale
        self.transition_scale = transition_scale
        self.self_loop_scale = self_loop_scale
        self.beam = beam
        self.retry_beam = retry_beam
        self.careful = careful

        self.num_done = 0
        self.num_error = 0
        self.num_retry = 0
        self.total_likelihood = 0
        self.total_frames = 0
        self.disambiguation_symbols = (
            disambiguation_symbols if disambiguation_symbols is not None else []
        )
        if self.beam >= self.retry_beam:
            self.retry_beam = 4 * self.beam

    def boost_silence(
        self, silence_weight: float, silence_phones: typing.List[int], only_silence: bool = True
    ):
        """
        Function to boost probabilities associated with silence states in the GMM

        Parameters
        ----------
        silence_weight: float
            Factor to boost silence by, 1.0 means no boosting, less than 1.0 decreases silence state probability,
            greater than 1.0 increases silence probability
        silence_phones: list[int]
            Phone IDs corresponding to silence phones
        only_silence: bool
            Flag for whether to boost only states that are associated with silence phones and not speech phones
        """
        if only_silence:
            self.acoustic_model.boost_only_silence(
                self.transition_model, silence_phones, silence_weight
            )
        else:
            self.acoustic_model.boost_silence(
                self.transition_model, silence_phones, silence_weight
            )

    def align_utterance(
        self,
        training_graph: VectorFst,
        features: FloatMatrix,
        utterance_id: str = None,
        reference_phones: typing.List[typing.List[int]] = None,
    ) -> typing.Optional[Alignment]:
        """

        Parameters
        ----------
        training_graph: :class:`~_kalpy.fstext.VectorFst`
            Training graph for the utterance
        features: :class:`~_kalpy.matrix.FloatMatrix`
            Feature matrix for the utterance
        utterance_id: str, optional
            Identifier for the utterance to store
        reference_phones: list[list[int]], optional
            Sequence of phones to use as reference and constrain alignments to only transition IDs corresponding to the
            phones specified for each frame

        Returns
        -------
        :class:`~kalpy.gmm.data.Alignment` or None
            Alignment object with list of transition IDs and other information for the utterance. If the utterance could
            not be aligned, returns None

        """
        if reference_phones is None:
            (
                alignment,
                words,
                likelihood,
                per_frame_log_likelihoods,
                successful,
                retried,
            ) = gmm_align_compiled(
                self.transition_model,
                self.acoustic_model,
                training_graph,
                features,
                acoustic_scale=self.acoustic_scale,
                transition_scale=self.transition_scale,
                self_loop_scale=self.self_loop_scale,
                beam=self.beam,
                retry_beam=self.retry_beam,
                careful=self.careful,
            )
        else:
            logger.debug(f"Using reference phones in alignment for {utterance_id}")
            assert len(reference_phones) == features.NumRows()
            (
                alignment,
                words,
                likelihood,
                per_frame_log_likelihoods,
                successful,
                retried,
            ) = gmm_align_reference_phones(
                self.transition_model,
                self.acoustic_model,
                training_graph,
                features,
                reference_phones,
                acoustic_scale=self.acoustic_scale,
                transition_scale=self.transition_scale,
                self_loop_scale=self.self_loop_scale,
                beam=self.beam,
                retry_beam=self.retry_beam,
                careful=self.careful,
            )
            if successful:
                redo = False
                alignment_phones = [
                    self.transition_model.TransitionIdToPhone(x) for x in alignment
                ]
                if len(reference_phones) != len(alignment):
                    logger.debug(
                        f"Mismatched alignment and reference length: {len(alignment)} vs {len(reference_phones)}"
                    )
                for i in range(len(reference_phones)):
                    if (
                        alignment_phones[i] not in reference_phones[i]
                        and -1 not in reference_phones[i]
                    ):
                        logger.debug(
                            f"Mismatch in frame {i}! {alignment_phones[i]} should be {reference_phones[i]}"
                        )
                        redo = True
                        reference_phones[i].append(-1)
                if redo:
                    logger.debug(f"Redoing {utterance_id} with more lenient reference phones")
                    (
                        alignment,
                        words,
                        likelihood,
                        per_frame_log_likelihoods,
                        successful,
                        retried,
                    ) = gmm_align_reference_phones(
                        self.transition_model,
                        self.acoustic_model,
                        training_graph,
                        features,
                        reference_phones,
                        acoustic_scale=self.acoustic_scale,
                        transition_scale=self.transition_scale,
                        self_loop_scale=self.self_loop_scale,
                        beam=self.beam,
                        retry_beam=self.retry_beam,
                        careful=self.careful,
                    )
                    for i in range(len(reference_phones)):
                        if (
                            alignment_phones[i] not in reference_phones[i]
                            and -1 not in reference_phones[i]
                        ):
                            logger.debug(
                                f"Mismatch in frame {i}! {alignment_phones[i]} should be {reference_phones[i]}"
                            )
        if not successful:
            return None
        if retried and utterance_id:
            logger.debug(f"Retried {utterance_id}")
        return Alignment(utterance_id, alignment, words, likelihood, per_frame_log_likelihoods)

    def align_utterances(
        self,
        training_graph_archive: FstArchive,
        feature_archive: FeatureArchive,
        reference_phone_archive: RandomAccessInt32VectorVectorReader = None,
    ) -> typing.Generator[Alignment]:
        """
        Function for aligning all utterances in a training graph archive and feature archive

        Parameters
        ----------
        training_graph_archive: :class:`~kalpy.decoder.data.FstArchive`
            Archive of training graph FSTs per utterance
        feature_archive: :class:`~kalpy.feat.data.FeatureArchive`
            Archive of feature matrices per utterance
        reference_phone_archive: :class:`~_kalpy.util.RandomAccessInt32VectorVectorReader`, optional
            Archive of reference phone sequences per utterance

        Yields
        ------
        :class:`~kalpy.gmm.data.Alignment`
            Successful alignments, skipping utterances that could not be aligned
        """
        logger.debug(f"Aligning with {self.acoustic_model_path}")
        num_done = 0
        num_error = 0
        total_frames = 0
        total_likelihood = 0
        for utterance_id, feats in feature_archive:
            if feats.NumRows() == 0:
                logger.warning(f"Skipping {utterance_id} due to zero-length features")
                continue
            try:
                training_graph = training_graph_archive[utterance_id]
            except KeyError:
                logger.warning(f"Skipping {utterance_id} due to missing training graph")
                continue

            reference_phones = None
            if reference_phone_archive is not None:
                if reference_phone_archive.HasKey(utterance_id):
                    reference_phones = reference_phone_archive.Value(utterance_id)
            try:
                logger.debug(f"Processing {utterance_id}")
                alignment = self.align_utterance(
                    training_graph, feats, utterance_id, reference_phones
                )
                if alignment is None:
                    yield utterance_id, None
                    num_error += 1
                    continue
                yield alignment
                total_likelihood += alignment.likelihood
                total_frames += len(alignment.alignment)
                num_done += 1
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                logger.warning(f"Error on {utterance_id}: {e}")
                traceback_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                logger.debug("\n".join(traceback_lines))
        if total_frames:
            logger.info(
                f"Overall log-likelihood per frame is {total_likelihood / total_frames} over {total_frames} frames."
            )
        logger.info(f"Done {num_done}, errors on {num_error}")

    def export_alignments(
        self,
        file_name: typing.Union[pathlib.Path, str],
        training_graph_archive: FstArchive,
        feature_archive: FeatureArchive,
        reference_phone_archive: RandomAccessInt32VectorVectorReader = None,
        word_file_name: typing.Union[pathlib.Path, str] = None,
        likelihood_file_name: typing.Union[pathlib.Path, str] = None,
        write_scp: bool = False,
        callback: typing.Callable = None,
    ) -> None:
        """
        Export alignments from training graph and features archives to an alignment archive file

        Parameters
        ----------
        file_name: str or :class:`~pathlib.Path`
            Alignment archive file path
        training_graph_archive: :class:`~kalpy.decoder.data.FstArchive`
            Archive of training graph FSTs per utterance
        feature_archive: :class:`~kalpy.feat.data.FeatureArchive`
            Archive of feature matrices per utterance
        reference_phone_archive: :class:`~_kalpy.util.RandomAccessInt32VectorVectorReader`, optional
            Archive of reference phone sequences per utterance
        word_file_name: str or :class:`~pathlib.Path`, optional
            File path to save word sequence
        likelihood_file_name: str or :class:`~pathlib.Path`, optional
            File path to save per frame log-likelihoods
        write_scp: boolean
            Flag for whether to write alignment archive with SCP file, defaults to False
        callback: callable, optional
            Callback to emit :class:`~kalpy.gmm.data.Alignment` objects as they're processed
        """
        write_specifier = generate_write_specifier(file_name, write_scp)
        writer = Int32VectorWriter(write_specifier)
        word_writer = None
        if word_file_name:
            word_write_specifier = generate_write_specifier(word_file_name, write_scp)
            word_writer = Int32VectorWriter(word_write_specifier)
        likelihood_writer = None
        if likelihood_file_name:
            likelihood_write_specifier = generate_write_specifier(likelihood_file_name, write_scp)
            likelihood_writer = BaseFloatVectorWriter(likelihood_write_specifier)
        try:
            for alignment in self.align_utterances(
                training_graph_archive,
                feature_archive,
                reference_phone_archive=reference_phone_archive,
            ):
                if alignment is None:
                    continue
                if isinstance(alignment, tuple):
                    if callback:
                        callback(alignment)
                    continue
                if callback:
                    callback((alignment.utterance_id, alignment.likelihood))
                writer.Write(str(alignment.utterance_id), alignment.alignment)
                if word_writer is not None:
                    word_writer.Write(str(alignment.utterance_id), alignment.words)
                if likelihood_writer is not None:
                    likelihood_writer.Write(
                        str(alignment.utterance_id), alignment.per_frame_likelihoods
                    )
        except Exception as e:
            logger.error(e)
            raise
        finally:
            writer.Close()
            if word_writer is not None:
                word_writer.Close()
            if likelihood_writer is not None:
                likelihood_writer.Close()
