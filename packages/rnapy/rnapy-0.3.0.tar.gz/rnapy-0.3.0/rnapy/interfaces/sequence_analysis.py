import os
from typing import Dict, Any, List, Union

import numpy as np

from ..core.exceptions import ModelNotFoundError, PredictionError
from ..core.factory import ModelFactory
from ..utils.file_utils import save_npy_file, process_sequence_input


class SequenceAnalysisInterface:
    def __init__(self, model_factory: ModelFactory, loaded_models: Dict[str, Any] = None):
        self.factory = model_factory
        self.loaded_models = loaded_models or {}

    def update_loaded_models(self, loaded_models: Dict[str, Any]):
        self.loaded_models = loaded_models

    def analyze_sequence(self, sequences: Union[str, List[str]],
                         analysis_type: str = "full",
                         model: str = "rna-fm",
                         **kwargs) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Comprehensive sequence analysis
        
        Args:
            sequences: RNA sequences or FASTA file path
            analysis_type: Analysis type ("full", "properties", "embedding", "structure")
            model: Model name
            **kwargs: Additional parameters
            
        Returns:
            Analysis results - single dict for single sequence, list for multiple
        """
        try:
            if model not in self.loaded_models:
                raise ModelNotFoundError(f"Model '{model}' is not loaded. Please load the model first.")

            model_instance = self.loaded_models[model]
            
            # Process input (handle FASTA files)
            sequence_ids, sequence_list = process_sequence_input(sequences)
            is_single_sequence = isinstance(sequences, str) and not sequences.endswith(('.fasta', '.fa', '.fas'))
            
            results_list = []
            for i, (seq_id, sequence) in enumerate(zip(sequence_ids, sequence_list)):
                results = {
                    'sequence': sequence,
                    'sequence_id': seq_id,
                    'length': len(sequence),
                    'analysis_type': analysis_type
                }

                if analysis_type in ["full", "properties"]:
                    results.update(self._analyze_basic_properties(sequence))

                # Extract embeddings
                if analysis_type in ["full", "embedding"]:
                    embeddings = model_instance.extract_embeddings([sequence])
                    results['embeddings'] = embeddings[0]
                    results['embedding_stats'] = {
                        'shape': embeddings[0].shape,
                        'mean': float(np.mean(embeddings[0])),
                        'std': float(np.std(embeddings[0]))
                    }

                # Predict structure
                if analysis_type in ["full", "structure"]:
                    structure_results = model_instance.predict(
                        sequence,
                        return_embeddings=False,
                        return_contacts=True,
                        return_attention=False
                    )

                    if 'secondary_structure' in structure_results and structure_results['secondary_structure']:
                        structure = structure_results['secondary_structure'][0]
                        results['secondary_structure'] = structure
                        results['structure_info'] = self._analyze_structure(structure)

                    if 'contacts' in structure_results:
                        results['contacts'] = structure_results['contacts'][0]

                results_list.append(results)
            
            return results_list[0] if is_single_sequence else results_list

        except Exception as e:
            raise PredictionError(f"Sequence analysis failed: {str(e)}")

    def extract_embeddings(self, sequences: Union[str, List[str]],
                           model: str = "rna-fm",
                           layer: int = 12,
                           format: str = "raw",
                           save_dir: str = None,
                           **kwargs) -> Union[np.ndarray, List[np.ndarray]]:
        """Extract embeddings for sequences
        
        Args:
            sequences: RNA sequences or FASTA file path
            model: Model name
            layer: Layer number for extraction
            format: Format ("raw", "mean", "bos")
            save_dir: File path to save embeddings
            **kwargs: Additional parameters
            
        Returns:
            Embeddings array or list of arrays
        """
        try:
            if model not in self.loaded_models:
                raise ModelNotFoundError(f"Model '{model}' is not loaded. Please load the model first.")

            model_instance = self.loaded_models[model]
            
            # Process input (handle FASTA files)
            sequence_ids, sequence_list = process_sequence_input(sequences)
            is_single_input = isinstance(sequences, str) and not sequences.endswith(('.fasta', '.fa', '.fas'))

            embeddings = model_instance.extract_embeddings(sequence_list, layer, format)
            
            # Handle save file
            for i, (seq_id, sequence) in enumerate(zip(sequence_ids, sequence_list)):
                if save_dir:
                    filename = f"{seq_id}_embeddings.npy" if is_single_input else f"{seq_id}_embeddings.npy"
                    filepath = os.path.join(save_dir, filename) if os.path.isdir(save_dir) else save_dir
                    save_npy_file(embeddings[i], filepath)

            return embeddings[0] if is_single_input else embeddings

        except Exception as e:
            raise PredictionError(f"Embedding extraction failed: {str(e)}")

    def compare_sequences(self, seq1: Union[str, List[str]], seq2: Union[str, List[str]],
                          model: str = "rna-fm",
                          comparison_type: str = "full",
                          embedding_format: str = "raw",
                          **kwargs) -> Dict[str, Any]:
        """Compare two sequences or sequence sets
        
        Args:
            seq1: First sequence(s) or FASTA file
            seq2: Second sequence(s) or FASTA file
            model: Model name
            comparison_type: Comparison type ("full", "sequence", "embedding", "structure")
            embedding_format: Format ("raw", "mean", "bos")
            **kwargs: Additional parameters
            
        Returns:
            Comparison results
        """
        try:
            # Process both inputs
            ids1, seqs1 = process_sequence_input(seq1)
            ids2, seqs2 = process_sequence_input(seq2)
            
            # For simplicity, compare first sequences if multiple provided
            seq1_str = seqs1[0]
            seq2_str = seqs2[0]
            
            results = {
                'sequence1': seq1_str,
                'sequence2': seq2_str,
                'sequence1_id': ids1[0],
                'sequence2_id': ids2[0],
                'lengths': [len(seq1_str), len(seq2_str)],
                'comparison_type': comparison_type,
                'embedding_format': embedding_format
            }

            # Sequence similarity
            results['sequence_similarity'] = self._calculate_sequence_similarity(seq1_str, seq2_str)

            # Embedding similarity
            if comparison_type in ["full", "embedding"]:
                emb1 = self.extract_embeddings(seq1_str, model, format=embedding_format, **kwargs)
                emb2 = self.extract_embeddings(seq2_str, model, format=embedding_format, **kwargs)
                results['embedding_similarity'] = self._calculate_embedding_similarity(emb1, emb2)

            # Structure similarity
            if comparison_type in ["full", "structure"]:
                if model not in self.loaded_models:
                    raise ModelNotFoundError(f"Model '{model}' is not loaded. Please load the model first.")

                model_instance = self.loaded_models[model]

                struct1 = model_instance.predict_secondary_structure([seq1_str])
                struct2 = model_instance.predict_secondary_structure([seq2_str])

                if struct1 and struct2:
                    results['structure_similarity'] = self._calculate_structure_similarity(struct1[0], struct2[0])
                    results['structures'] = [struct1[0], struct2[0]]

            return results

        except Exception as e:
            raise PredictionError(f"Sequence comparison failed: {str(e)}")

    def batch_analyze(self, sequences: Union[str, List[str]],
                      analysis_type: str = "full",
                      model: str = "rna-fm",
                      **kwargs) -> List[Dict[str, Any]]:
        """Batch analyze multiple sequences
        
        Args:
            sequences: RNA sequences or FASTA file path
            analysis_type: Analysis type ("full", "properties", "embedding", "structure")
            model: Model name
            **kwargs: Additional parameters
            
        Returns:
            List of analysis results
        """
        # Process input
        sequence_ids, sequence_list = process_sequence_input(sequences)
        
        results = []
        for i, (seq_id, sequence) in enumerate(zip(sequence_ids, sequence_list)):
            try:
                result = self.analyze_sequence(sequence, analysis_type, model, **kwargs)
                if isinstance(result, list):
                    result = result[0]  # Single sequence should return single result
                result['sequence_index'] = i
                results.append(result)

            except Exception as e:
                results.append({
                    'sequence_index': i,
                    'sequence': sequence,
                    'sequence_id': seq_id,
                    'error': str(e),
                    'failed': True
                })

        return results

    def _analyze_basic_properties(self, sequence: str) -> Dict[str, Any]:
        seq_upper = sequence.upper()
        length = len(sequence)

        return {
            'gc_content': (seq_upper.count('G') + seq_upper.count('C')) / length,
            'composition': {
                'A': seq_upper.count('A') / length,
                'U': seq_upper.count('U') / length,
                'G': seq_upper.count('G') / length,
                'C': seq_upper.count('C') / length
            },
            'purine_content': (seq_upper.count('A') + seq_upper.count('G')) / length,
            'pyrimidine_content': (seq_upper.count('C') + seq_upper.count('U')) / length
        }

    def _analyze_structure(self, structure: str) -> Dict[str, Any]:
        return {
            'length': len(structure),
            'paired_bases': structure.count('(') + structure.count(')'),
            'unpaired_bases': structure.count('.'),
            'pairing_ratio': (structure.count('(') + structure.count(')')) / len(structure),
            'stem_count': self._count_stems(structure)
        }

    def _count_stems(self, structure: str) -> int:
        stem_count = 0
        in_stem = False

        for char in structure:
            if char == '(' and not in_stem:
                stem_count += 1
                in_stem = True
            elif char == '.' and in_stem:
                in_stem = False

        return stem_count

    def _calculate_sequence_similarity(self, seq1: str, seq2: str) -> float:
        if not seq1 or not seq2:
            return 0.0

        min_len = min(len(seq1), len(seq2))
        matches = sum(1 for i in range(min_len) if seq1[i].upper() == seq2[i].upper())

        return matches / max(len(seq1), len(seq2))

    def _calculate_embedding_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        if emb1.ndim > 1:
            emb1_mean = np.mean(emb1, axis=0)
        else:
            emb1_mean = emb1

        if emb2.ndim > 1:
            emb2_mean = np.mean(emb2, axis=0)
        else:
            emb2_mean = emb2

        dot_product = np.dot(emb1_mean, emb2_mean)
        norm1 = np.linalg.norm(emb1_mean)
        norm2 = np.linalg.norm(emb2_mean)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    def _calculate_structure_similarity(self, struct1: str, struct2: str) -> float:
        if len(struct1) != len(struct2):
            min_len = min(len(struct1), len(struct2))
            matches = sum(1 for i in range(min_len) if struct1[i] == struct2[i])
            return matches / max(len(struct1), len(struct2))
        else:
            matches = sum(1 for i in range(len(struct1)) if struct1[i] == struct2[i])
            return matches / len(struct1)
