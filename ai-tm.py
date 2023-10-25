import os
import logging
import argparse
from pathlib import Path
import json

from project import analyze_project
from architecture import ArchitectureAnalyzer
from architecture_reviewer import ArchitectureReviewer
from llms import LLMWrapper
from user_story import analyze_user_story

import constants
    
BASEDIR = os.environ.get('GITHUB_WORKSPACE')
if not BASEDIR:
    BASEDIR=os.getcwd()
        
def main():
    parser = argparse.ArgumentParser(
        prog='ai-tm.py',
        description='AI featured threat modeling and security review',
        epilog='Experimental. Use on your own risk'
    )
    parser.add_argument("type", type=str, choices=['project', 'architecture', 'user-story'], help="type of feature")
    parser.add_argument("--provider", type=str, choices=['openai', 'openrouter'], help="provider of LLM API, default: openai", default="openai")
    parser.add_argument("--inputs", type=str, help="file path or json array of paths to input files (depends on feature)", nargs='?')
    parser.add_argument("--output", type=str, help="path to output file", nargs='?')
    parser.add_argument("-ai", "--architecture-inputs", type=str, help="for user-story only: json array of paths to architecture files", nargs='?')
    parser.add_argument("-atmi", "--architecture-threat-model-input", type=str, help="for user-story only: path to architecture threat model file", nargs='?')
    parser.add_argument("--model", type=str, help="type of ChatGPT model, default: gpt-4", default="gpt-4")
    parser.add_argument("--temperature", type=float, help="sampling temperature for a model, default 0.2", default=0.2)
    parser.add_argument('-v', '--verbose', action='store_true', help="turn on verbose messages, default: false", default="false")
    parser.add_argument('-d', '--debug', action='store_true', help="turn on debug messages, default: false", default="false")
    parser.add_argument("-usos", "--user-story-output-suffix", type=str, help="for user-story only: suffix that will be added to input file name to create output file, default: _SECURITY", default="_SECURITY")
    parser.add_argument("-t", "--template-dir", type=str, help="path to template dir, default: ./templates", default="./templates")
    parser.add_argument("--review", action='store_true', help="review input files using LLM, default: false", default="false")
    parser.add_argument("--create-draft", action='store_true', help="create draft of input (e.g. architecture) based on files (e.g. README.md,controllers.go,swagger.yaml), default: false", default="false")

    args = parser.parse_args()

    if args.verbose is True:
        logging.basicConfig(level=logging.INFO)
        
    if args.debug is True:
        logging.basicConfig(level=logging.DEBUG)
        
    logging.debug(f'running for feature: {args.type}...')

    if args.type == "project":
        if not args.inputs:
            inputs = [Path(BASEDIR).joinpath(constants.PROJECT_INPUT)]
        else:
            raw_input_paths = json.loads(args.inputs)
            inputs = [Path(BASEDIR).joinpath(p) for p in raw_input_paths]
        
        if not args.output:
            output = Path(BASEDIR).joinpath(constants.PROJECT_OUTPUT)
        else:
            output = Path(BASEDIR).joinpath(args.output)
        analyze_project(args, inputs, output)

    if args.type == "architecture" and args.review is True:
        if not args.inputs:
            inputs = Path(BASEDIR).joinpath(constants.ARCHITECTURE_INPUT)
        else:
            inputs = Path(BASEDIR).joinpath(args.inputs)
        
        if not args.output:
            output = Path(BASEDIR).joinpath(constants.ARCHITECTURE_REVIEW)
        else:
            output = Path(BASEDIR).joinpath(args.output)
            
        return ArchitectureReviewer(LLMWrapper(args)).review_architecture(args, inputs, output)

    if args.type == "architecture":
        if not args.inputs:
            inputs = [Path(BASEDIR).joinpath(constants.ARCHITECTURE_INPUT)]
        else:
            raw_input_paths = json.loads(args.inputs)
            inputs = [Path(BASEDIR).joinpath(p) for p in raw_input_paths]
        
        if not args.output:
            output = Path(BASEDIR).joinpath(constants.ARCHITECTURE_OUTPUT)
        else:
            output = Path(BASEDIR).joinpath(args.output)
            
        ArchitectureAnalyzer(LLMWrapper(args)).analyze_architecture(args, inputs, output)

    if args.type == "user-story":
        if not args.inputs:
            parser.error("inputs cannot be empty for user-story")
        raw_input_paths = json.loads(args.inputs)
        
        inputs = [Path(BASEDIR).joinpath(p) for p in raw_input_paths]
        inputs = [i for i in inputs if i.exists()]
        
        logging.debug(f'inputs for process: {len(inputs)}')
        
        for i in inputs:
            if not args.output:
                filename, file_extension = os.path.splitext(str(i.resolve()))
                output = Path(filename + args.user_story_output_suffix + file_extension)
            else:
                parser.error("output is forbidden for user-story, it will be generated based on input")
            logging.debug(f'output set to: {output}')
        
            if not args.architecture_inputs:
                architecture_inputs = [Path(BASEDIR).joinpath(constants.ARCHITECTURE_INPUT)]
            else:
                architecture_raw_input_paths = json.loads(args.architecture_inputs)
                architecture_inputs = [Path(BASEDIR).joinpath(p) for p in architecture_raw_input_paths]
                
            if not args.architecture_threat_model_input:
                architecture_tm_input = Path(BASEDIR).joinpath(constants.ARCHITECTURE_OUTPUT)
            else:
                architecture_tm_input = Path(BASEDIR).joinpath(args.architecture_threat_model_input)
            
            analyze_user_story(args, i, architecture_inputs, architecture_tm_input, output)

if __name__ == "__main__":
    main()
        