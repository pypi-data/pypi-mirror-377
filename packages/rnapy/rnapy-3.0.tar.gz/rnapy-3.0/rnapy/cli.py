#!/usr/bin/env python3
import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Union, List, Any


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format='%(levelname)s: %(message)s',
        level=level
    )


def parse_sequence_input(seq: Optional[str], fasta: Optional[str]) -> Union[str, List[str]]:
    """Parse sequence input from command line arguments"""
    if seq and fasta:
        raise ValueError("Cannot specify both --seq and --fasta")
    if not seq and not fasta:
        raise ValueError("Must specify either --seq or --fasta")
    
    if seq:
        # Handle comma-separated sequences
        if ',' in seq:
            return [s.strip() for s in seq.split(',')]
        return seq

    if fasta:
        # Return fasta file path, will be processed by toolkit
        return fasta
    # Should be unreachable due to checks above; keep for type checkers
    raise RuntimeError("Unreachable: invalid sequence input state")



def save_output(data: Any, save_dir: Optional[str], filename: str, format_type: str = "json") -> Optional[str]:
    """Save output data to file if save_dir is specified"""
    if not save_dir:
        return None

    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    if format_type == "json":
        output_file = save_path / f"{filename}.json"
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return str(output_file)
    elif format_type == "npy":
        import numpy as np
        output_file = save_path / f"{filename}.npy"
        np.save(output_file, data)
        return str(output_file)

    return None


def print_summary(data: Any, command: str):
    """Print summary of results to terminal"""
    if command == "seq_embed":
        if isinstance(data, list):
            print(f"Extracted embeddings for {len(data)} sequences")
        else:
            print(f"Extracted embedding with shape: {data.shape}")
    elif command == "struct_predict":
        if isinstance(data, list):
            print(f"Predicted structures for {len(data)} sequences")
        else:
            if 'secondary_structure' in data:
                print(f"Secondary structure: {data['secondary_structure']}")
            elif 'structure_file' in data:
                print(f"3D structure saved to: {data['structure_file']}")
    elif command == "invfold_gen":
        print(f"Generated {len(data.get('sequences', []))} sequences")
        for i, seq in enumerate(data.get('sequences', [])):
            print(f"Sequence {i+1}: {seq[:50]}...")
    elif command == "msa_features":
        if isinstance(data, dict):
            for key, value in data.items():
                if hasattr(value, 'shape'):
                    print(f"{key}: shape {value.shape}")
        else:
            print(f"MSA features shape: {data.shape}")
    elif command == "msa_analyze":
        print("MSA analysis completed:")
        for key, value in data.items():
            if key == 'consensus_sequence':
                print(f"Consensus: {value}")
            elif key == 'conservation_scores' and hasattr(value, 'mean'):
                print(f"Mean conservation: {value.mean():.3f}")


def _get_toolkit(config_dir: str = "configs", device: str = "cpu"):
    """Lazy import and initialize RNAToolkit"""
    try:
        from .toolkit import RNAToolkit
        from .core.config_loader import config_loader
        
        # Update config_dir if specified
        if config_dir != 'configs':
            config_loader.config_dir = Path(config_dir)
        
        return RNAToolkit(config_dir=config_dir, device=device), config_loader
    except ImportError as e:
        raise ImportError(f"Failed to import RNAToolkit. Missing dependencies: {e}")


def cmd_seq_embed(args):
    """Handle seq embed command"""
    sequences = parse_sequence_input(args.seq, args.fasta)
    
    toolkit, config_loader = _get_toolkit(args.config_dir, args.device)
    toolkit.load_model(args.model, args.model_path)
    
    embeddings = toolkit.extract_embeddings(
        sequences=sequences,
        model=args.model,
        layer=args.layer,
        format=args.format,
        save_dir=args.save_dir
    )

    if args.save_dir:
        print(f"Embeddings saved to: {args.save_dir}")

    print_summary(embeddings, "seq_embed")


def cmd_struct_predict(args):
    """Handle struct predict command"""
    sequences = parse_sequence_input(args.seq, args.fasta)

    # Infer structure type from model if not specified
    structure_type = args.structure_type
    if not structure_type:
        if args.model == "rhofold":
            structure_type = "3d"
        elif args.model in ["rna-fm", "mrna-fm", "rna_fm", "mrna_fm"]:
            structure_type = "2d"
        else:
            structure_type = "2d"  # Default

    toolkit, config_loader = _get_toolkit(args.config_dir, args.device)
    toolkit.load_model(args.model, args.model_path)

    results = toolkit.predict_structure(
        sequences=sequences,
        structure_type=structure_type,
        model=args.model,
        save_dir=args.save_dir
    )

    if args.save_dir:
        print(f"Structure prediction results saved to: {args.save_dir}")

    print_summary(results, "struct_predict")


def cmd_invfold_gen(args):
    """Handle invfold gen command"""
    if not args.pdb:
        raise ValueError("Must specify --pdb for inverse folding")
    
    toolkit, config_loader = _get_toolkit(args.config_dir, args.device)
    toolkit.load_model(args.model, args.model_path)
    
    kwargs = {}
    if hasattr(args, 'ss_npy') and args.ss_npy:
        kwargs['secondary_structure_file'] = args.ss_npy
    if hasattr(args, 'n_samples') and args.n_samples:
        kwargs['n_samples'] = args.n_samples
    
    results = toolkit.generate_sequences_from_structure(
        structure_file=args.pdb,
        model=args.model,
        save_dir=args.save_dir,
        **kwargs
    )
    
    if args.save_dir:
        print(f"Generated sequences saved to: {args.save_dir}")
    
    print_summary(results, "invfold_gen")


def cmd_msa_features(args):
    """Handle msa features command"""
    sequences = parse_sequence_input(args.seq, args.fasta)

    toolkit, config_loader = _get_toolkit(args.config_dir, args.device)
    toolkit.load_model(args.model, args.model_path)

    features = toolkit.extract_msa_features(
        sequences=sequences,
        feature_type=args.feature_type,
        model=args.model,
        layer=args.layer,
        save_dir=args.save_dir
    )

    if args.save_dir:
        print(f"MSA features saved to: {args.save_dir}")

    print_summary(features, "msa_features")


def cmd_msa_analyze(args):
    """Handle msa analyze command"""
    sequences = parse_sequence_input(args.seq, args.fasta)
    
    # Convert single sequence or fasta file to list for MSA analysis
    if isinstance(sequences, str):
        if sequences.endswith(('.fasta', '.fa', '.fas')):
            # Will be handled by toolkit
            pass
        else:
            raise ValueError("MSA analysis requires multiple sequences or FASTA file")

    toolkit, config_loader = _get_toolkit(args.config_dir, args.device)
    toolkit.load_model(args.model, args.model_path)

    results = toolkit.analyze_msa(
        msa_sequences=sequences,
        model=args.model,
        extract_consensus=args.extract_consensus,
        extract_conservation=args.extract_conservation,
        save_dir=args.save_dir
    )

    if args.save_dir:
        print(f"MSA analysis results saved to: {args.save_dir}")

    print_summary(results, "msa_analyze")


def add_global_args(parser):
    """Add global arguments to a parser"""
    parser.add_argument('--device', choices=['cpu', 'cuda'], default='cpu',
                       help='Computing device (default: cpu)')
    parser.add_argument('--model', 
                       choices=['rna-fm', 'mrna-fm', 'rhofold', 'ribodiffusion', 'rhodesign', 'rna-msm'],
                       required=True,
                       help='Model to use')
    parser.add_argument('--model-path', required=True,
                       help='Path to model checkpoint')
    parser.add_argument('--config-dir', default='configs',
                       help='Configuration directory (default: configs)')
    parser.add_argument('--provider-config',
                       help='Path to provider-specific configuration file')
    parser.add_argument('--seed', type=int,
                       help='Random seed')
    parser.add_argument('--save-dir',
                       help='Output directory for results')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')


def create_parser():
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        prog='rnapy',
        description='RNA analysis toolkit command line interface'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # seq embed command
    seq_parser = subparsers.add_parser('seq', help='Sequence analysis commands')
    seq_subparsers = seq_parser.add_subparsers(dest='seq_command')

    embed_parser = seq_subparsers.add_parser('embed', help='Extract sequence embeddings')
    add_global_args(embed_parser)
    embed_parser.add_argument('--seq', help='RNA sequence(s) (comma-separated for multiple)')
    embed_parser.add_argument('--fasta', help='FASTA file path')
    embed_parser.add_argument('--layer', type=int, default=-1,
                             help='Layer to extract from (default: -1)')
    embed_parser.add_argument('--format', choices=['raw', 'mean', 'bos'], default='mean',
                             help='Embedding format (default: mean)')

    # struct predict command
    struct_parser = subparsers.add_parser('struct', help='Structure prediction commands')
    struct_subparsers = struct_parser.add_subparsers(dest='struct_command')

    predict_parser = struct_subparsers.add_parser('predict', help='Predict RNA structure')
    add_global_args(predict_parser)
    predict_parser.add_argument('--seq', help='RNA sequence(s) (comma-separated for multiple)')
    predict_parser.add_argument('--fasta', help='FASTA file path')
    predict_parser.add_argument('--structure-type', choices=['2d', '3d'],
                               help='Structure type (inferred from model if not specified)')

    # invfold gen command
    invfold_parser = subparsers.add_parser('invfold', help='Inverse folding commands')
    invfold_subparsers = invfold_parser.add_subparsers(dest='invfold_command')

    gen_parser = invfold_subparsers.add_parser('gen', help='Generate sequences from structure')
    add_global_args(gen_parser)
    gen_parser.add_argument('--pdb', required=True, help='PDB structure file')
    gen_parser.add_argument('--ss-npy', help='Secondary structure NPY file (for RhoDesign)')
    gen_parser.add_argument('--n-samples', type=int, default=1,
                           help='Number of sequences to generate (default: 1)')

    # msa commands
    msa_parser = subparsers.add_parser('msa', help='MSA analysis commands')
    msa_subparsers = msa_parser.add_subparsers(dest='msa_command')

    features_parser = msa_subparsers.add_parser('features', help='Extract MSA features')
    add_global_args(features_parser)
    features_parser.add_argument('--seq', help='RNA sequence(s) (comma-separated for multiple)')
    features_parser.add_argument('--fasta', help='FASTA file path')
    features_parser.add_argument('--feature-type', choices=['embeddings', 'attention', 'both'],
                                default='embeddings', help='Feature type (default: embeddings)')
    features_parser.add_argument('--layer', type=int, default=-1,
                                help='Layer to extract from (default: -1)')

    analyze_parser = msa_subparsers.add_parser('analyze', help='Analyze MSA')
    add_global_args(analyze_parser)
    analyze_parser.add_argument('--seq', help='RNA sequence(s) (comma-separated for multiple)')
    analyze_parser.add_argument('--fasta', help='FASTA file path')
    analyze_parser.add_argument('--extract-consensus', action='store_true',
                               help='Extract consensus sequence')
    analyze_parser.add_argument('--extract-conservation', action='store_true',
                               help='Calculate conservation scores')

    return parser


def main():
    """Main CLI entry point"""
    parser = create_parser()
    
    # Handle case where no arguments are provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)

    # Handle missing subcommands
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Set random seed if provided
    if args.seed:
        import random
        import numpy as np
        random.seed(args.seed)
        np.random.seed(args.seed)

    try:
        # Dispatch to appropriate command handler
        if args.command == 'seq' and args.seq_command == 'embed':
            cmd_seq_embed(args)
        elif args.command == 'struct' and args.struct_command == 'predict':
            cmd_struct_predict(args)
        elif args.command == 'invfold' and args.invfold_command == 'gen':
            cmd_invfold_gen(args)
        elif args.command == 'msa' and args.msa_command == 'features':
            cmd_msa_features(args)
        elif args.command == 'msa' and args.msa_command == 'analyze':
            cmd_msa_analyze(args)
        else:
            parser.print_help()
            sys.exit(1)

    except Exception as e:
        if args.verbose:
            raise
        else:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
