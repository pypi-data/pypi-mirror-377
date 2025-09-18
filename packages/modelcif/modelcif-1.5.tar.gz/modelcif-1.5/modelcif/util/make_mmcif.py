#!/usr/bin/env python3

"""
Add minimal ModelCIF-related tables to an mmCIF file.

Given any mmCIF file as input, this script will add any missing
ModelCIF-related tables and write out a new file that is minimally compliant
with the ModelCIF dictionary.

This is done by simply reading in the original file with python-modelcif and
then writing it out again, so
  a) any data in the input file that is not understood by python-modelcif
     will be lost on output; and
  b) input files that aren't compliant with the PDBx dictionary, or that
     contain syntax errors or other problems, may crash or otherwise confuse
     python-modelcif.

While a best effort is made, it is not guaranteed that the output file is
valid. It is recommended that it is run through a validator such as
examples/validate_mmcif.py and any errors corrected or reported as
issues.
"""


import modelcif.reader
import modelcif.dumper
import modelcif.model
import ihm.util
import os
import argparse


def add_modelcif_info(s):
    if not s.title:
        s.title = 'Auto-generated system'
    if not s.protocols:
        default_protocol = modelcif.protocol.Protocol()
        step = modelcif.protocol.ModelingStep(
            name='modeling', input_data=None, output_data=None)
        default_protocol.steps.append(step)
        s.protocols.append(default_protocol)

    for model_group in s.model_groups:
        for model in model_group:
            # Entity description is also used by python-modelcif for
            # ma_data.name, which is mandatory, so it cannot be unknown/?
            for asym in model.assembly:
                if asym.entity.description is ihm.unknown:
                    asym.entity.description = "target"

            model.not_modeled_residue_ranges.extend(
                _get_not_modeled_residues(model))
    return s


def _get_not_modeled_residues(model):
    """Yield NotModeledResidueRange objects for all residue ranges in the
       Model that are not referenced by Atom objects"""
    for assem in model.assembly:
        asym = assem.asym if hasattr(assem, 'asym') else assem
        if not asym.entity.is_polymeric():
            continue
        # Make a set of all residue indices of this asym "handled"
        # by being modeled with Atom objects
        handled_residues = set()
        for atom in model._atoms:
            if atom.asym_unit is asym:
                handled_residues.add(atom.seq_id)
        # Convert set to a list of residue ranges
        handled_residues = ihm.util._make_range_from_list(
            sorted(handled_residues))
        # Return not-modeled for each non-handled range
        for r in ihm.util._invert_ranges(handled_residues,
                                         end=assem.seq_id_range[1],
                                         start=assem.seq_id_range[0]):
            yield modelcif.model.NotModeledResidueRange(asym, r[0], r[1])


def get_args():
    p = argparse.ArgumentParser(
        description="Add minimal ModelCIF-related tables to an mmCIF file.")
    p.add_argument("input", metavar="input.cif", help="input mmCIF file name")
    p.add_argument("output", metavar="output.cif",
                   help="output mmCIF file name",
                   default="output.cif", nargs="?")
    return p.parse_args()


def main():
    args = get_args()

    if (os.path.exists(args.input) and os.path.exists(args.output)
            and os.path.samefile(args.input, args.output)):
        raise ValueError("Input and output are the same file")

    with open(args.input) as fh:
        with open(args.output, 'w') as fhout:
            modelcif.dumper.write(
                fhout,
                [add_modelcif_info(s) for s in modelcif.reader.read(fh)])


if __name__ == '__main__':
    main()
