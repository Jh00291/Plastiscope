#!/bin/bash

# Define variables
TSV_URL="https://plasticdb.org/static/degraders_list.tsv"
TSV_FILE="degraders_list.tsv"
ORGANISM_LIST="organism_names.txt"
GENOME_DIR="$HOME/jacob/genomes"

# Step 1: Download the TSV file ONLY if it doesn't exist
if [[ ! -f "$TSV_FILE" ]]; then
    echo "Downloading microorganism data from PlasticDB..."
    wget --content-disposition -O "$TSV_FILE" "$TSV_URL"
else
    echo "TSV file already exists. Skipping download."
fi

# Step 2: Extract organism names (only if the list is missing)
if [[ ! -f "$ORGANISM_LIST" ]]; then
    echo "Extracting organism names..."
    awk -F'\t' 'NR > 1 {print $1}' "$TSV_FILE" | sort | uniq > "$ORGANISM_LIST"
else
    echo "Organism names file already exists. Skipping extraction."
fi

# Step 3: Create genome directory if it doesn't exist
mkdir -p "$GENOME_DIR"

# Step 4: Download the best available genome for each organism
echo "Downloading genomes..."
while IFS= read -r organism; do
    if [[ -n "$organism" ]]; then
        echo "Fetching genome for: $organism"
        sanitized_name="${organism// /_}"  # Replace spaces with underscores
        genome_file="$GENOME_DIR/${sanitized_name}.fasta"

        if [[ -f "$genome_file" ]]; then
            echo "Genome for '$organism' already exists. Skipping..."
        else
            zip_file="$GENOME_DIR/${sanitized_name}.zip"

            # Attempt to download the RefSeq genome
            datasets download genome taxon "$organism" \
                --include genome \
                --assembly-source refseq \
                --assembly-level complete \
                --filename "$zip_file"

            # If RefSeq is unavailable or ZIP is empty, try GenBank
            if [[ ! -s "$zip_file" ]]; then
                echo "RefSeq unavailable, trying GenBank genome for $organism..."
                datasets download genome taxon "$organism" \
                    --include genome \
                    --assembly-source genbank \
                    --assembly-level complete \
                    --filename "$zip_file"
            fi

            # Extract only the .fna file and move it to genomes directory
            if [[ -s "$zip_file" ]]; then
                unzip -o "$zip_file" -d "$GENOME_DIR"

                # Find the extracted .fna file and move it to genomes directory
                fna_file=$(find "$GENOME_DIR" -type f -name "*.fna" | head -n 1)
                if [[ -f "$fna_file" ]]; then
                    mv "$fna_file" "$genome_file"
                    echo "Genome saved: $genome_file"
                else
                    echo "No .fna file found for $organism. Skipping..."
                fi

                # Clean up unnecessary files
                rm "$zip_file"
                find "$GENOME_DIR" -type d -empty -delete
            else
                echo "No genome found for $organism"
            fi
        fi
    fi
done < "$ORGANISM_LIST"

echo "Genome downloads complete. All FASTA files are in '$GENOME_DIR'."

