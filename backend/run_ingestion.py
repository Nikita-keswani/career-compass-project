import argparse
from src.scripts.ingest_data import ingest_directory

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest data from a directory into Pinecone")
    parser.add_argument("directory", help="Absolute path to the directory containing files to ingest")
    parser.add_argument("index_name", help="Name of the index to ingest data into")
    
    args = parser.parse_args()
    ingest_directory(args.directory, args.index_name)