
#!/usr/bin/env python3
"""AI Highlighter System v2.0 - Main Entry Point
Analyzes Twitch VODs, detects highlights, generates vertical clips.
"""
import os
import sys
import argparse
import logging
import uvicorn

def main():
    parser = argparse.ArgumentParser(description="AI Highlighter System v2.0")
    sub = parser.add_subparsers(dest="command")

    # Analyze command
    analyze = sub.add_parser("analyze", help="Analyze a Twitch VOD")
    analyze.add_argument("--vod-url", required=True, help="Twitch VOD URL")
    analyze.add_argument("--media-path", required=True, help="Path to media file")
    analyze.add_argument("--config", default=None, help="Config file path")

    # Server command
    server = sub.add_parser("server", help="Start the API server")
    server.add_argument("--host", default="0.0.0.0")
    server.add_argument("--port", type=int, default=8000)
    server.add_argument("--config", default=None)

    # Dashboard command
    dash = sub.add_parser("dashboard", help="Generate dashboard HTML")
    dash.add_argument("--output", default="output/dashboard.html")
    dash.add_argument("--config", default=None)

    # Test command
    test_cmd = sub.add_parser("test", help="Run test suite")

    args = parser.parse_args()

    from modules.config import PipelineConfig
    from modules.logging_config import setup_logging

    if args.command == "analyze":
        config = PipelineConfig.load(args.config) if args.config else PipelineConfig()
        setup_logging(config.log_level, config.log_file, config.base_dir)
        from modules.pipeline import HighlighterPipeline
        pipeline = HighlighterPipeline(config)
        results = pipeline.run(args.vod_url, args.media_path)
        print(f"Analysis complete: {results['total_clips']} clips generated")

    elif args.command == "server":
        config = PipelineConfig.load(args.config) if args.config else PipelineConfig()
        setup_logging(config.log_level, config.log_file, config.base_dir)
        from modules.api import create_app
        app = create_app(config)
        uvicorn.run(app, host=args.host, port=args.port)

    elif args.command == "dashboard":
        config = PipelineConfig.load(args.config) if args.config else PipelineConfig()
        from modules.dashboard import DashboardGenerator
        gen = DashboardGenerator(config)
        html = gen.generate_dashboard()
        gen.save_dashboard(html, args.output)
        print(f"Dashboard saved to {args.output}")

    elif args.command == "test":
        import unittest
        loader = unittest.TestLoader()
        suite = loader.discover("tests", pattern="test_*.py")
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(suite)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
