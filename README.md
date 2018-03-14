# food-microbiome-habitats

## Format bacteria habitat predictions for the FoodMicrobiome project

Sources (not included in the repo):
  * PubMed abstracts
  * GenBank
  * DSMZ
  * CIRM

Named entity recognition (taxon names and habitat mentions), normalization (habitats) and relation extraction (*lives in*): [openminted/UC-AS-C](https://github.com/openminted/uc-tdm-AS-C).

`make -n output/food-microbiome-habitats`

`prepare-food-microbiome.py` : main script for building the table. It requires the following resources:

`resources/taxa+id_Bacteria.txt` : synonym map of bacteria taxa.

`predictions/PubMed_lives-in.txt`, `predictions/genbank_mappings.txt`, `predictions/dsmz-taxon-habitat-mappings.txt`, `predictions/CIRM_08022018.txt` : taxon-habitat predictions.

`etc/habitat-focus.txt` : identifier and label for habitat focus concepts.


## Explore and prepare BioSample input

### File dimension reduction

**Goal**: filter bacteria samples and split into several files.

`make -n resources/biosample-split`

`resources/biosample_set.xml` : complete BioSample as downloaded from NCBI.

### Explore the usage of Attributes

**Goal**: inventory of all Attributes used in BioSample entries.

`make -n output/biosample-attributes-count.txt`

### Explore candidate Attributes for habitats

**Goal**: evaluate the amount of habitat information found in BioSample.

`make -n output/biosample-table.txt`
