PREPARE=./prepare-food-microbiome.py
TAXA=taxa+id_Bacteria.txt
HABITAT=habitat-focus.txt
PUBMED=PubMed_lives-in.txt
GENBANK=genbank_mappings.txt
DSMZ=dsmz-taxon-habitat-mappings.txt
CIRM=CIRM_08022018.txt

TARGET=food-microbiome-habitats_01.txt food-microbiome-habitats_03.txt food-microbiome-habitats_05.txt food-microbiome-habitats_02.txt food-microbiome-habitats_04.txt food-microbiome-habitats_06.txt

all: $(PREPARE) $(TAXA) $(HABITAT) $(PUBMED) $(GENBANK) $(DSMZ) $(CIRM)
	./$^

clean:
	$(RM) $(TARGET)
