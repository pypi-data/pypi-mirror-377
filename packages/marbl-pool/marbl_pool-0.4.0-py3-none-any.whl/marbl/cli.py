import argparse
import logging
from pathlib import Path

from .main import process_variants

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Matrix assignment of rare variants using bayesian logic"
    )

    parser.add_argument("--vcf-folder", default=".", help="VCF file folder")
    parser.add_argument("--mpileup-folder", default=".", help="mpileup file folder")
    parser.add_argument(
        "--sampletable",
        default=".",
        help="Sampletable (tsv) with sample ids and dimension specification (row/column)."
    )
    parser.add_argument(
        "--decodetable",
        default="",
        help="decodetable (tsv) with sample ids and pool combinations (row/column)."
    )
    parser.add_argument("--output", default=".", help="Output directory")
    parser.add_argument(
        "--verbose", action="store_true", default=True, help="Verbose logging"
    )

    parser.add_argument("--use-fallback", action="store_true", default=False,
                        help="Enable fallback mode")
    parser.add_argument("--use-custom-cand-strength", action="store_true", default=False,
                        help="Use custom candidate strength")
    parser.add_argument("--use-custom-other-strength", action="store_true", default=False,
                        help="Use custom other strength")

    parser.add_argument("--prior-odds", type=int, default=10,
                        help="Prior odds (default: 10)")
    parser.add_argument("--cand-strength", type=int, default=100,
                        help="Candidate strength (default: 100)")
    parser.add_argument("--other-strength", type=int, default=1000,
                        help="Other strength (default: 1000)")
    parser.add_argument("--bg-strength", type=int, default=30000,
                        help="Background strength (default: 30000)")

    parser.add_argument("--theta-cand-max", type=float, default=0.4,
                        help="Maximum candidate theta (default: 0.4)")
    parser.add_argument("--theta-bg-max", type=float, default=0.1,
                        help="Maximum background theta (default: 0.1)")

    parser.add_argument("--posterior-estimator-prior", type=int, default=1000,
                        help="Posterior estimator prior (default: 1000)")
    parser.add_argument("--max-threads", type=int, default=0,
                        help="Maximum threads (uses all available as default)")

    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    process_variants(
        sampletable=Path(args.sampletable),
        decodetable=Path(args.decodetable) if args.decodetable else "",
        vcf_dir=Path(args.vcf_folder),
        mpileup_dir=Path(args.mpileup_folder),
        output_dir=output_dir,
        use_fallback=args.use_fallback,
        use_custom_cand_strength=args.use_custom_cand_strength,
        use_custom_other_strength=args.use_custom_other_strength,
        prior_odds=args.prior_odds,
        cand_strength=args.cand_strength,
        other_strength=args.other_strength,
        bg_strength=args.bg_strength,
        theta_cand_max=args.theta_cand_max,
        theta_bg_max=args.theta_bg_max,
        posterior_estimator_prior=args.posterior_estimator_prior,
        max_threads=args.max_threads,
    )


if __name__ == "__main__":
    main()