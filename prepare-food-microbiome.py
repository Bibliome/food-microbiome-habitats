#!/bin/env python

from sys import stdin, stderr, argv

def log(msg, *args):
    stderr.write(msg % args)
    stderr.write('\n')

class Habitats(dict):
    def __init__(self, *args):
        dict.__init__(self, *args)

    def add(self, obtid, obtname, source, form):
        if obtid in self:
            habitat = self[obtid]
        else:
            habitat = Habitat(obtid, obtname)
            self[obtid] = habitat
        habitat.sources.add(source)
        habitat.forms.add(form)

class Habitat:
    def __init__(self, obtid, name):
        self.obtid = obtid
        self.name = name
        self.forms = set()
        self.sources = set()
        self.strains = []

SUPERSOURCES = ('bib', 'db')

class Taxon:
    def __init__(self, taxid, name, species):
        self.taxid = taxid
        self.name = name
        self.habitats = dict((ss, Habitats()) for ss in SUPERSOURCES)
        self.focus_habitats = dict((ss, Habitats()) for ss in SUPERSOURCES)
        self.species = species

    @classmethod
    def load(klass, taxa_fn):
        f = open(taxa_fn)
        for line in f:
            syn, taxid, canonical, path, pos, rank, spid, spname = line.split('\t')
            if rank == 'species' and taxid not in Species.ALL:
                Species(taxid, canonical)
            elif rank == 'no rank' and spid != '' and taxid not in Strain.ALL:
                Strain(taxid, canonical, spid)
        f.close()

    def has_habitat(self):
        for ss in SUPERSOURCES:
            if len(self.habitats[ss]) > 0:
                return True
        return False

    def get_habitats(self, supersource, focus):
        if focus:
            return self.focus_habitats[supersource]
        return self.habitats[supersource]

    def rank(self):
        raise NotImplementedError

    def habitat_string(self, habitat):
        raise NotImplementedError

    def line(self, supersource):
        return '\t'.join((
            self.taxid,
            self.rank(),
            self.species.name,
            self.name,
            supersource,
            ', '.join(self.habitat_string(h) for h in self.get_habitats(supersource, False).itervalues()),
            ', '.join(self.habitat_string(h) for h in self.get_habitats(supersource, True).itervalues()),
            ', '.join(', '.join(h.forms) for h in self.habitats[supersource].itervalues()),
            ', '.join(', '.join(h.sources) for h in self.habitats[supersource].itervalues())
        ))

class Species(Taxon):
    ALL = {}
    
    def __init__(self, taxid, name):
        Taxon.__init__(self, taxid, name, self)
        self.strains = []
        Species.ALL[taxid] = self

    def rank(self):
        return 'species'

    def habitat_string(self, habitat):
        return '%s (%d)' % (habitat.name, len(habitat.strains))
        
class Strain(Taxon):
    ALL = {}
    
    def __init__(self, taxid, name, spid):
        Taxon.__init__(self, taxid, name, spid)
        Strain.ALL[taxid] = self

    def rank(self):
        return 'strain'

    def habitat_string(self, habitat):
        return habitat.name

    def _aggregate_to_species(self, supersource, focus):
        habitats = self.get_habitats(supersource, focus)
        for habitat in habitats.itervalues():
            sphabs = self.species.get_habitats(supersource, focus)
            if habitat.obtid in sphabs:
                sphab = sphabs[habitat.obtid]
            else:
                sphab = Habitat(habitat.obtid, habitat.name)
                sphabs[habitat.obtid] = sphab
            sphab.strains.append(self)

    def aggregate_to_species(self):
        for ss in SUPERSOURCES:
            self._aggregate_to_species(ss, False)
            self._aggregate_to_species(ss, True)

class TabularRelationReader:
    def __init__(self, supersource, source_prefix, taxid, obtid, obtname, source, obtform, obtpath):
        self.supersource = supersource
        self.source_prefix = source_prefix
        self.taxid = taxid
        self.obtid = obtid
        self.obtname = obtname
        self.source = source
        self.obtform = obtform
        self.obtpath = obtpath

    def _col(self, cols, col):
        if col is None:
            return '???'
        return cols[col].strip()

    def read_line(self, line):
        cols = line.split('\t')
        taxid = self._col(cols, self.taxid)
        obtid = self._col(cols, self.obtid)
        obtname = self._col(cols, self.obtname)
        source = self.source_prefix + self._col(cols, self.source)
        obtform = self._col(cols, self.obtform)
        obtpath = self._col(cols, self.obtpath)
        self.add_relation(self.supersource, taxid, obtid, obtname, source, obtform, obtpath)

    def read_file(self, fn):
        f = open(fn)
        for line in f:
            self.read_line(line)
        f.close()
        
    def get_focus_name(self, obtpath):
        for obtid, obtname in HABITAT_FOCUS:
            if obtpath.endswith('/' + obtid) or '/'+obtid+'/' in obtpath:
                return obtid, obtname
        return None, None

    def get_taxon(self, taxid):
        if taxid in Species.ALL:
            return Species.ALL[taxid]
        if taxid in Strain.ALL:
            return Strain.ALL[taxid]
        return None

    def add_relation(self, supersource, taxid, obtid, obtname, source, obtform, obtpath):
        taxon = self.get_taxon(taxid)
        if taxon is not None:
            taxon.habitats[supersource].add(obtid, obtname, source, obtform)
            focusid, focusname = self.get_focus_name(obtpath)
            if focusid is not None:
                taxon.focus_habitats[supersource].add(focusid, focusname, source, obtform)
        
_, TAXA_FN, HABITAT_FOCUS_FN, RELS_FN, GB_FN, DSMZ_FN, CIRM_FN = argv

log('loading taxon file: %s', TAXA_FN)
Taxon.load(TAXA_FN)
log('%d species, %d strains', len(Species.ALL), len(Strain.ALL))

log('loading habitat focus: %s', HABITAT_FOCUS_FN)
f=open(HABITAT_FOCUS_FN)
HABITAT_FOCUS = tuple(line.strip().split('\t') for line in f)
f.close()

log('reading PubMed relations: %s' % RELS_FN)
PUBMED_READER = TabularRelationReader('bib', 'pmid:', taxid=3, obtid=8, obtname=11, source=1, obtform=9, obtpath=12)
PUBMED_READER.read_file(RELS_FN)

STANDARD_COLUMNS = {
    'taxid': 2,
    'obtid': 5,
    'obtname': 6,
    'source': 8,
    'obtform': 4,
    'obtpath': 7
}
log('reading GenBank relations: %s' % GB_FN)
GENBANK_READER = TabularRelationReader('db', 'gb:', **STANDARD_COLUMNS)
GENBANK_READER.read_file(GB_FN)

log('reading DSMZ relations: %s' % DSMZ_FN)
DSMZ_READER = TabularRelationReader('db', 'dsmz:', **STANDARD_COLUMNS)
DSMZ_READER.read_file(DSMZ_FN)

log('reading CIRM relations: %s' % CIRM_FN)
CIRM_READER = TabularRelationReader('db', 'cirm:', taxid=2, obtid=5, obtname=6, source=None, obtform=4, obtpath=7)
CIRM_READER.read_file(CIRM_FN)

log('aggregating species')
for strain in Strain.ALL.itervalues():
    try:
        strain.species = Species.ALL[strain.species]
        strain.species.strains.append(strain)
        strain.aggregate_to_species()
    except KeyError:
        log('!! no species: %s', strain.species)

class FoodMicrobiomeWriter:
    HEADERS = ('TAXON ID', 'RANK', 'SPECIES', 'TAXON NAME', 'SOURCE TYPE', 'HABITATS', 'FOOD', 'SURFACE FORMS', 'SOURCES')

    def __init__(self, max_taxa, fn_pattern = 'output/food-microbiome-habitats/food-microbiome-habitats_%02d.txt'):
        self.max_taxa = max_taxa
        self.fn_pattern = fn_pattern
        self.ntaxa = 0
        self.filei = 0
        self.f = None

    def next_file(self):
        if self.f is not None:
            self.f.close()
        self.filei += 1
        self.ntaxa = 0
        fn = self.fn_pattern % self.filei
        log('writing %s', fn)
        self.f = open(fn, 'w')
        self.write_line('\t'.join(FoodMicrobiomeWriter.HEADERS))

    def write_line(self, line):
        self.f.write(line)
        self.f.write('\n')

    def write_files(self):
        self.next_file()
        for species in sorted(Species.ALL.values(), lambda a, b: cmp(a.name, b.name)):
            if self.ntaxa >= self.max_taxa:
                self.next_file()
            if species.has_habitat():
                self.ntaxa += 1
                for ss in SUPERSOURCES:
                    self.write_line(species.line(ss))
                for strain in species.strains:
                    if strain.has_habitat():
                        self.ntaxa += 1
                        for ss in SUPERSOURCES:
                            self.write_line(strain.line(ss))
        self.f.close()

writer = FoodMicrobiomeWriter(10000)
writer.write_files()
