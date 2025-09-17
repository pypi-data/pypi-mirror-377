import logging
from typing import Dict, Any, List, Union, Optional

import numpy as np
from pathlib import Path

from rnapy.core import ConfigManager, ModelFactory
from rnapy.core.config_loader import config_loader
from rnapy.core.exceptions import ModelLoadError
from rnapy.interfaces import StructurePredictionInterface, SequenceAnalysisInterface, InverseFoldingInterface, MSAAnalysisInterface
from rnapy.providers.RiboDiffusion import RiboDiffusionAdapter
from rnapy.providers.rhofold import RhoFoldAdapter
from rnapy.providers.rna_fm import RNAFMAdapter, RNAFMPredictor
from rnapy.providers.rhodesign import RhoDesignAdapter
from rnapy.providers.rna_msm import RnaMSMAdapter, RnaMSMPredictor


class RNAToolkit:
    def __init__(self, config_dir: str = "configs", device: str = "cpu"):
        """Initialize RNA toolkit

        Args:
            config_dir: Configuration directory
            device: Computing device ("cpu" or "cuda")
        """
        self.device = device
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize configuration manager
        self.config_manager = ConfigManager(config_dir)
        try:
            config_loader.config_dir = Path(config_dir)
        except Exception:
            pass
        self.config_manager.create_default_configs()

        # Initialize model factory
        self.model_factory = ModelFactory()
        self._register_models()

        # Cache loaded models
        self._loaded_models = {}

        # Initialize interfaces
        self.structure_predictor = StructurePredictionInterface(self.model_factory, self._loaded_models)
        self.sequence_analyzer = SequenceAnalysisInterface(self.model_factory, self._loaded_models)
        self.inverse_folder = InverseFoldingInterface(self.model_factory, self._loaded_models)
        self.msa_analyzer = MSAAnalysisInterface(self.model_factory, self._loaded_models)

        self.logger.info(f"RNAToolkit initialized with device: {device}")

    def _register_models(self):
        """Register all available models"""
        # RNA-FM models
        self.model_factory.register_model("rna-fm", RNAFMAdapter)
        self.model_factory.register_model("rna_fm", RNAFMAdapter)  # Compatibility alias
        self.model_factory.register_model("mrna-fm", RNAFMAdapter)
        self.model_factory.register_model("mrna_fm", RNAFMAdapter)  # Compatibility alias
        
        # RhoFold models  
        self.model_factory.register_model("rhofold", RhoFoldAdapter)
        self.model_factory.register_model("rho-fold", RhoFoldAdapter)  # Compatibility alias
        self.model_factory.register_model("rhofold+", RhoFoldAdapter)  # For RhoFold+ variant
        
        # RiboDiffusion models
        self.model_factory.register_model("ribodiffusion", RiboDiffusionAdapter)
        self.model_factory.register_model("ribo-diffusion", RiboDiffusionAdapter)  # Compatibility alias
        
        # RhoDesign models
        self.model_factory.register_model("rhodesign", RhoDesignAdapter)
        self.model_factory.register_model("rho-design", RhoDesignAdapter)  # Compatibility alias
        
        # RNA-MSM models
        self.model_factory.register_model("rna-msm", RnaMSMAdapter)
        self.model_factory.register_model("rna_msm", RnaMSMAdapter)  # Compatibility alias

    def load_model(self, model_name: str, checkpoint_path: str, **kwargs) -> None:
        """Load pretrained model

        Args:
            model_name: Model name (e.g., 'rna-fm', 'mrna-fm')
            checkpoint_path: Model checkpoint file path
            **kwargs: Additional configuration parameters
        """
        try:
            # Merge configurations using new config loader
            base_config = config_loader.load_global_config()
            
            # Load provider-specific config
            normalized_model_name = model_name.replace('-', '_')
            if normalized_model_name in ['rna_fm']:
                provider_config = config_loader.load_provider_config("rna_fm", **kwargs)
            elif normalized_model_name in ['mrna_fm']:
                provider_config = config_loader.load_provider_config("mrna_fm", **kwargs)
            elif normalized_model_name in ['rhofold', 'rho_fold']:
                provider_config = config_loader.load_provider_config("rhofold", **kwargs)
            elif normalized_model_name in ['ribodiffusion', 'ribo_diffusion']:
                provider_config = config_loader.load_provider_config("ribodiffusion", **kwargs)
            elif normalized_model_name in ['rhodesign', 'rho_design']:
                provider_config = config_loader.load_provider_config("rhodesign", **kwargs)
            elif normalized_model_name in ['rna_msm', 'rna_msm']:
                provider_config = config_loader.load_provider_config("rna_msm", **kwargs)
            else:
                # For unknown models, use base config with kwargs
                provider_config = base_config
                provider_config.update(kwargs)
            
            # Use provider config as the final config (it already includes merged settings)
            config = provider_config

            # Create model
            model = self.model_factory.create_model(model_name, config, self.device)

            # Load checkpoint
            model.load_model(checkpoint_path)

            # Cache model
            self._loaded_models[model_name] = model

            # Update model references in interfaces
            self.structure_predictor.update_loaded_models(self._loaded_models)
            self.sequence_analyzer.update_loaded_models(self._loaded_models)
            self.inverse_folder.update_loaded_models(self._loaded_models)
            self.msa_analyzer.update_loaded_models(self._loaded_models)

            self.logger.info(f"Successfully loaded model: {model_name}")

        except Exception as e:
            raise ModelLoadError(f"Failed to load model {model_name}: {str(e)}")

    def analyze_sequence(self, sequences: Union[str, List[str]],
                         model: str = "rna-fm",
                         analysis_type: str = "full",
                         **kwargs) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Comprehensive sequence analysis
        
        Args:
            sequences: RNA sequences or FASTA file path
            model: Model name to use
            analysis_type: Analysis type ('full', 'embedding', 'structure', 'properties')
            **kwargs: Additional parameters
        
        Returns:
            Analysis results - single dict or list of dicts
        """
        self._ensure_model_loaded(model)
        return self.sequence_analyzer.analyze_sequence(sequences, analysis_type, model, **kwargs)

    def predict_structure(self, sequences: Union[str, List[str]],
                          structure_type: str = "2d",
                          model: str = "rna-fm",
                          threshold: float = 0.5,
                          save_dir: Optional[str] = None,
                          **kwargs) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Predict RNA structure
        
        Args:
            sequences: RNA sequences or FASTA file path
            structure_type: Structure type ("2d" or "3d")
            model: Model name to use
            threshold: Contact probability threshold (for 2D structure only)
            save_dir: File path to save results (CT format for single sequence)
            **kwargs: Additional parameters
        
        Returns:
            Structure prediction results
        """
        self._ensure_model_loaded(model)

        if structure_type == "2d":
            return self.structure_predictor.predict_2d_structure(sequences, model, threshold, save_dir=save_dir, **kwargs)
        elif structure_type == "3d":
            return self.structure_predictor.predict_3d_structure(sequences, model=model, save_dir=save_dir, **kwargs)
        else:
            raise ValueError(f"Unsupported structure type: {structure_type}")

    def extract_embeddings(self, sequences: Union[str, List[str]],
                           model: str = "rna-fm",
                           layer: int = 12,
                           format: str = "raw",
                           save_dir: Optional[str] = None,
                           **kwargs) -> Union[np.ndarray, List[np.ndarray]]:
        """Extract sequence embeddings
        
        Args:
            sequences: RNA sequences or FASTA file path
            model: Model name to use
            layer: Layer number to extract
            format: Embedding format ("raw", "mean", "bos")
            save_dir: File path to save embeddings (.npy for single, .npz for multiple)
            **kwargs: Additional parameters
        
        Returns:
            Embedding representation array(s)
        """
        self._ensure_model_loaded(model)
        return self.sequence_analyzer.extract_embeddings(sequences, model, layer, format, save_dir=save_dir, **kwargs)

    def compare_sequences(self, seq1: Union[str, List[str]], seq2: Union[str, List[str]],
                          model: str = "rna-fm",
                          comparison_type: str = "full",
                          embedding_format: str = "raw",
                          **kwargs) -> Dict[str, Any]:
        """Compare two sequences
        
        Args:
            seq1: First sequence(s) or FASTA file
            seq2: Second sequence(s) or FASTA file
            model: Model name to use
            comparison_type: Comparison type ("full", "embedding", "structure")
            embedding_format: Embedding format ("raw", "mean", "bos")
            **kwargs: Additional parameters
        
        Returns:
            Comparison results dictionary
        """
        self._ensure_model_loaded(model)
        return self.sequence_analyzer.compare_sequences(seq1, seq2, model, comparison_type, embedding_format, **kwargs)

    def batch_analyze(self, sequences: Union[str, List[str]],
                      analysis_type: str = "full",
                      model: str = "rna-fm",
                      **kwargs) -> List[Dict[str, Any]]:
        """Batch sequence analysis
        
        Args:
            sequences: RNA sequences or FASTA file path
            analysis_type: Analysis type
            model: Model name to use
            **kwargs: Additional parameters
        
        Returns:
            List of analysis results
        """
        self._ensure_model_loaded(model)
        return self.sequence_analyzer.batch_analyze(sequences, analysis_type, model, **kwargs)

    def predict_secondary_structure(self, sequences: Union[str, List[str]],
                                    threshold: float = 0.5,
                                    model: str = "rna-fm",
                                    advanced_postprocess: bool = True,
                                    allow_noncanonical: bool = True,
                                    **kwargs) -> Union[str, List[str]]:
        """Predict secondary structure
        
        Args:
            sequences: RNA sequences or FASTA file path
            threshold: Contact probability threshold
            model: Model name to use
            advanced_postprocess: Use advanced post-processing
            allow_noncanonical: Allow non-canonical base pairs
            **kwargs: Additional parameters
        
        Returns:
            Dot-bracket format secondary structure(s)
        """
        self._ensure_model_loaded(model)

        # Get model instance and handle FASTA input processing
        from .utils.file_utils import process_sequence_input
        sequence_ids, sequence_list = process_sequence_input(sequences)
        
        model_instance = self._loaded_models[model]
        structures = model_instance.predict_secondary_structure(
            sequence_list, threshold, advanced_postprocess, allow_noncanonical
        )
        
        # Return single structure if single input
        is_single_input = isinstance(sequences, str) and not sequences.endswith(('.fasta', '.fa', '.fas'))
        return structures[0] if is_single_input else structures

    def save_ct_files(self, sequences: Union[str, List[str]],
                      output_dir: str,
                      sequence_ids: Optional[List[str]] = None,
                      model: str = "rna-fm",
                      threshold: float = 0.5,
                      advanced_postprocess: bool = True,
                      allow_noncanonical: bool = True,
                      **kwargs) -> List[str]:
        """Generate and save CT files
        
        Args:
            sequences: RNA sequences or FASTA file path
            output_dir: Output directory
            sequence_ids: Optional sequence identifiers
            model: Model name to use
            threshold: Contact probability threshold
            advanced_postprocess: Use advanced post-processing
            allow_noncanonical: Allow non-canonical base pairs
            **kwargs: Additional parameters
        
        Returns:
            List of generated CT file paths
        """
        self._ensure_model_loaded(model)

        # Process input to get sequences and IDs
        from .utils.file_utils import process_sequence_input
        auto_ids, sequence_list = process_sequence_input(sequences)
        
        # Use provided IDs or auto-generated ones
        if sequence_ids is None:
            sequence_ids = auto_ids

        model_instance = self._loaded_models[model]
        return model_instance.save_ct_file(
            sequence_list, output_dir, sequence_ids,
            threshold, advanced_postprocess, allow_noncanonical
        )

    def predict_contacts(self, sequences: Union[str, List[str]],
                         model: str = "rna-fm",
                         threshold: float = 0.5,
                         return_processed: bool = True,
                         allow_noncanonical: bool = True,
                         **kwargs) -> Union[np.ndarray, List[np.ndarray]]:
        """Predict contact map
        
        Args:
            sequences: RNA sequences or FASTA file path
            model: Model name to use
            threshold: Contact probability threshold
            return_processed: Return processed contact map (with multiple pairing handling)
            allow_noncanonical: Allow non-canonical base pairs
            **kwargs: Additional parameters
        
        Returns:
            Contact map(s) - raw or processed
        """
        self._ensure_model_loaded(model)

        # Process input
        from .utils.file_utils import process_sequence_input
        sequence_ids, sequence_list = process_sequence_input(sequences)
        is_single_input = isinstance(sequences, str) and not sequences.endswith(('.fasta', '.fa', '.fas'))

        predictor = self.create_predictor(model)
        contacts = predictor.predict_contacts(
            sequence_list, threshold, return_processed, allow_noncanonical
        )
        
        return contacts[0] if is_single_input else contacts

    def analyze_structure_details(self, sequence: str,
                                  model: str = "rna-fm",
                                  threshold: float = 0.5,
                                  advanced_postprocess: bool = True,
                                  allow_noncanonical: bool = True,
                                  **kwargs) -> Dict[str, Any]:
        """Detailed structure analysis
        
        Args:
            sequence: RNA sequence
            model: Model name to use
            threshold: Contact threshold
            advanced_postprocess: Use advanced post-processing
            allow_noncanonical: Allow non-canonical base pairs
            **kwargs: Additional parameters
        
        Returns:
            Detailed structure analysis results
        """
        self._ensure_model_loaded(model)

        predictor = self.create_predictor(model)
        return predictor.analyze_structure_details(
            sequence, threshold, advanced_postprocess, allow_noncanonical
        )

    def create_predictor(self, model: str = "rna-fm"):
        """Create predictor instance
        
        Args:
            model: Model name
        
        Returns:
            Predictor instance
        """
        self._ensure_model_loaded(model)
        if model in ("rna-msm", "rna_msm"):
            return RnaMSMPredictor(self._loaded_models[model])
        else:
            return RNAFMPredictor(self._loaded_models[model])

    def get_model_info(self, model: str = None) -> Dict[str, Any]:
        """Get model information
        
        Args:
            model: Model name, if None returns info for all loaded models
        
        Returns:
            Model information dictionary
        """
        if model is None:
            return {
                name: model_instance.get_model_info()
                for name, model_instance in self._loaded_models.items()
            }
        else:
            if model in self._loaded_models:
                return self._loaded_models[model].get_model_info()
            else:
                return {"loaded": False, "available": model in self.model_factory.list_models()}

    def list_available_models(self) -> List[str]:
        """List all available models"""
        return self.model_factory.list_models()

    def list_loaded_models(self) -> List[str]:
        """List loaded models"""
        return list(self._loaded_models.keys())

    def generate_sequences_from_structure(self, structure_file: str,
                                         model: str = "ribodiffusion",
                                         n_samples: int = 1,
                                         save_dir: Optional[str] = None,
                                         **kwargs) -> Dict[str, Any]:
        """Generate RNA sequences from 3D structure (inverse folding)
        
        Args:
            structure_file: Path to PDB structure file
            model: Model name for inverse folding
            n_samples: Number of sequences to generate
            save_dir: Output directory for results
            **kwargs: Additional parameters
        
        Returns:
            Dictionary containing generated sequences and metadata
        """
        return self.inverse_folder.generate_sequences(
            structure_file=structure_file,
            model=model,
            n_samples=n_samples,
            output_dir=save_dir,
            **kwargs
        )

    def batch_generate_sequences_from_structures(self, structure_files: Union[List[str], str],
                                                model: str = "ribodiffusion",
                                                n_samples: int = 1,
                                                output_base_dir: Optional[str] = None,
                                                **kwargs) -> List[Dict[str, Any]]:
        """Generate sequences for multiple structures
        
        Args:
            structure_files: List of PDB files or directory containing PDB files
            model: Model name for inverse folding
            n_samples: Number of sequences to generate per structure
            output_base_dir: Base output directory
            **kwargs: Additional parameters
        
        Returns:
            List of results for each structure
        """
        return self.inverse_folder.batch_generate_sequences(
            structure_files=structure_files,
            model=model,
            n_samples=n_samples,
            output_base_dir=output_base_dir,
            **kwargs
        )

    def analyze_generated_sequences(self, generation_results: Dict[str, Any],
                                   include_structure_analysis: bool = True) -> Dict[str, Any]:
        """Analyze properties of generated sequences
        
        Args:
            generation_results: Results from generate_sequences_from_structure
            include_structure_analysis: Whether to predict secondary structure
        
        Returns:
            Analysis results
        """
        return self.inverse_folder.analyze_generated_sequences(
            generation_results=generation_results,
            include_structure_analysis=include_structure_analysis
        )

    def compare_with_native_sequence(self, generation_results: Dict[str, Any],
                                   native_sequence: Optional[str] = None) -> Dict[str, Any]:
        """Compare generated sequences with native sequence if available
        
        Args:
            generation_results: Results from generate_sequences_from_structure
            native_sequence: Native sequence for comparison (if available)
        
        Returns:
            Comparison results
        """
        return self.inverse_folder.compare_with_native_sequence(
            generation_results=generation_results,
            native_sequence=native_sequence
        )

    # MSA Analysis methods
    def extract_msa_features(self, sequences: Union[str, List[str]],
                            feature_type: str = "embeddings",
                            model: str = "rna-msm",
                            layer: int = -1,
                            save_dir: Optional[str] = None,
                            **kwargs) -> Union[np.ndarray, Dict[str, np.ndarray], Dict[str, Any]]:
        """Extract features from RNA sequences using MSA transformer
        
        Args:
            sequences: RNA sequence(s) or FASTA file path
            feature_type: Type of features ("embeddings", "attention", "both")
            model: Model name to use (default: rna-msm)
            layer: Layer to extract from (-1 for last layer)
            save_dir: Directory to save features
            **kwargs: Additional parameters
            
        Returns:
            Extracted features as numpy arrays or dict
        """
        self._ensure_model_loaded(model)
        return self.msa_analyzer.extract_msa_features(
            sequences=sequences,
            feature_type=feature_type,
            model=model,
            layer=layer,
            save_dir=save_dir,
            **kwargs
        )

    def analyze_msa(self, msa_sequences: List[str],
                   model: str = "rna-msm",
                   extract_consensus: bool = True,
                   extract_conservation: bool = True,
                   save_dir: Optional[str] = None,
                   **kwargs) -> Dict[str, Any]:
        """Analyze Multiple Sequence Alignment
        
        Args:
            msa_sequences: List of aligned RNA sequences
            model: Model name to use (default: rna-msm)
            extract_consensus: Extract consensus sequence
            extract_conservation: Calculate conservation scores
            save_dir: Directory to save analysis results
            **kwargs: Additional parameters
            
        Returns:
            MSA analysis results including features, consensus, conservation
        """
        self._ensure_model_loaded(model)
        return self.msa_analyzer.analyze_msa(
            msa_sequences=msa_sequences,
            model=model,
            extract_consensus=extract_consensus,
            extract_conservation=extract_conservation,
            save_dir=save_dir,
            **kwargs
        )

    def compare_sequences_msa(self, seq1: Union[str, List[str]], 
                             seq2: Union[str, List[str]],
                             model: str = "rna-msm",
                             comparison_method: str = "embedding_similarity",
                             **kwargs) -> Dict[str, Any]:
        """Compare sequences using MSA-based features
        
        Args:
            seq1: First sequence or MSA
            seq2: Second sequence or MSA
            model: Model name to use (default: rna-msm)
            comparison_method: Method for comparison
            **kwargs: Additional parameters
            
        Returns:
            Comparison results with similarity scores
        """
        self._ensure_model_loaded(model)
        return self.msa_analyzer.compare_sequences_msa(
            seq1=seq1,
            seq2=seq2,
            model=model,
            comparison_method=comparison_method,
            **kwargs
        )

    def extract_consensus_sequence(self, msa_sequences: List[str],
                                  model: str = "rna-msm",
                                  **kwargs) -> str:
        """Extract consensus sequence from MSA
        
        Args:
            msa_sequences: List of aligned RNA sequences
            model: Model name to use (default: rna-msm)
            **kwargs: Additional parameters
            
        Returns:
            Consensus sequence string
        """
        return self.msa_analyzer.extract_consensus_sequence(
            msa_sequences=msa_sequences,
            model=model,
            **kwargs
        )

    def calculate_conservation_scores(self, msa_sequences: List[str],
                                    **kwargs) -> List[float]:
        """Calculate conservation scores for each position in MSA
        
        Args:
            msa_sequences: List of aligned RNA sequences
            **kwargs: Additional parameters
            
        Returns:
            List of conservation scores (0-1, higher = more conserved)
        """
        return self.msa_analyzer.calculate_conservation_scores(
            msa_sequences=msa_sequences,
            **kwargs
        )

    def batch_msa_analysis(self, msa_list: List[List[str]],
                          model: str = "rna-msm",
                          extract_consensus: bool = True,
                          extract_conservation: bool = True,
                          **kwargs) -> List[Dict[str, Any]]:
        """Batch analyze multiple MSAs
        
        Args:
            msa_list: List of MSA sequences (each MSA is a list of sequences)
            model: Model name to use (default: rna-msm)
            extract_consensus: Extract consensus for each MSA
            extract_conservation: Calculate conservation for each MSA
            **kwargs: Additional parameters
            
        Returns:
            List of MSA analysis results
        """
        self._ensure_model_loaded(model)
        return self.msa_analyzer.batch_msa_analysis(
            msa_list=msa_list,
            model=model,
            extract_consensus=extract_consensus,
            extract_conservation=extract_conservation,
            **kwargs
        )

    def get_msa_statistics(self, msa_sequences: List[str]) -> Dict[str, Any]:
        """Get basic statistics for an MSA
        
        Args:
            msa_sequences: List of aligned RNA sequences
            
        Returns:
            MSA statistics including length, depth, composition
        """
        return self.msa_analyzer.get_msa_statistics(msa_sequences=msa_sequences)

    def unload_model(self, model: str) -> None:
        """Unload model
        
        Args:
            model: Model name
        """
        if model in self._loaded_models:
            del self._loaded_models[model]

            # Update model references in interfaces
            self.structure_predictor.update_loaded_models(self._loaded_models)
            self.sequence_analyzer.update_loaded_models(self._loaded_models)
            self.msa_analyzer.update_loaded_models(self._loaded_models)

            self.logger.info(f"Unloaded model: {model}")
        else:
            self.logger.warning(f"Model {model} was not loaded")

    def set_device(self, device: str) -> None:
        """Set computing device
        
        Args:
            device: Device name ("cpu" or "cuda")
        """
        self.device = device

        # Move loaded models to new device
        for name, model in self._loaded_models.items():
            if hasattr(model, 'model') and model.model is not None:
                model.model = model.model.to(device)
                model.device = device
                self.logger.info(f"Moved model {name} to {device}")

    def _ensure_model_loaded(self, model: str) -> None:
        """Ensure model is loaded"""
        if model not in self._loaded_models:
            raise ModelLoadError(f"Model {model} is not loaded. Call load_model() first.")

    def _setup_logging(self, level: str = "INFO"):
        """Setup logging"""
        logging.basicConfig(
            level=getattr(logging, level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def __repr__(self) -> str:
        loaded_models = list(self._loaded_models.keys())
        available_models = self.model_factory.list_models()

        return f"""RNAToolkit(
    device='{self.device}',
    loaded_models={loaded_models},
    available_models={available_models}
)"""
