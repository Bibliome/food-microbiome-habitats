PREPARE=./prepare-food-microbiome.py
SPLIT=/projet/maiage/save/textemig/projet-work/software/misc-utils/split.py
ALVISNLP=/projet/maiage/save/textemig/projet-work/software/install/alvisnlp/bin/alvisnlp

TAXA=taxa+id_Bacteria.txt
HABITAT=habitat-focus.txt
PUBMED=PubMed_lives-in.txt
GENBANK=genbank_mappings.txt
DSMZ=dsmz-taxon-habitat-mappings.txt
CIRM=CIRM_08022018.txt
BACTERIA_IDS=bacteria-ids.txt
BIOSAMPLE_ALL=biosample_set.xml

TARGET=food-microbiome-habitats_01.txt food-microbiome-habitats_03.txt food-microbiome-habitats_05.txt food-microbiome-habitats_02.txt food-microbiome-habitats_04.txt food-microbiome-habitats_06.txt

all: $(PREPARE) $(TAXA) $(HABITAT) $(PUBMED) $(GENBANK) $(DSMZ) $(CIRM)
	./$^

biosample-split: $(BIOSAMPLE_ALL) $(BACTERIA_IDS)
	mkdir -p $@
	$(SPLIT) --begin '<BioSample ' --end '</BioSample>' --header '<?xml version="1.0" encoding="UTF-8"?>\n<BioSampleSet>\n' --footer '</BioSampleSet>\n' --dictionary $(BACTERIA_IDS) -n 10000 --filter '<Organism taxonomy_id="(\d+)"' --pattern '$@/biosample-%06d.xml' $<

biosample-table.txt: biosample.plan biosample-split
	$(ALVISNLP) -log alvisnlp.log -verbose $<

clean:
	$(RM) $(TARGET)
