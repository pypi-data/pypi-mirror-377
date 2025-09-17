import argparse
import pandas as pd
from topsisx.pipeline import DecisionPipeline
from topsisx.reports import generate_report

def main():
    parser = argparse.ArgumentParser(description="Decision-making CLI with TOPSISX")
    parser.add_argument("input", help="Path to CSV input file")
    parser.add_argument("--weights", default="entropy", help="Weighting method (entropy, ahp, equal)")
    parser.add_argument("--method", default="topsis", help="Decision method (topsis, vikor, ahp)")
    parser.add_argument("--impacts", default="+,-", help="Impacts for criteria, e.g. +,-,+")
    parser.add_argument("--report", action="store_true", help="Generate PDF report")
    args = parser.parse_args()

    # Load CSV
    df = pd.read_csv(args.input)

    # Run pipeline
    pipe = DecisionPipeline(weights=args.weights, method=args.method)
    impacts = args.impacts.split(",") if args.impacts else None
    result = pipe.run(df.iloc[:, 1:], impacts=impacts)

    print(result)

    # Generate report
    if args.report:
        generate_report(result, method=args.method)

if __name__ == "__main__":
    main()
