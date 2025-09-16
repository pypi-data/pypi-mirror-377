from __future__ import annotations
from .part import AnnotatedPart, Annotation
from mesa_designer import TMD_DATA, AIP_DATA, SIGNAL_SEQS, NTEV_DATA, CTEV_DATA, TEVP_DATA, PRS_DATA

MESA_ORDER: list[str] = ["signal_peptide",
                         "tags",
                         "binder",
                         "tmd_linker",
                         "tmd",
                         "fret",
                         "protease",
                         "prs",
                         "cargo",
                         "aip"]


class MesaChain:
    def __init__(self) -> None:
        self.parts: dict[str, AnnotatedPart] = {}

    def get_parts(self) -> dict[str, AnnotatedPart]:
        return self.parts

    def add_binder(self, sequence: str, name: str | None = None, annotation: str | None = None) -> MesaChain:
        if not sequence:
            raise ValueError("Sequence cannot be None")

        self.parts["binder"] = AnnotatedPart(sequence=sequence,
                                             name=name if name else "Binder",
                                             seq_annotations=[Annotation("Binder" if not annotation else annotation)])

        return self

    def add_tmd_linker(self, sequence: str | None = None, name: str | None = None,
                       annotation: str | None = None) -> MesaChain:
        if not sequence:
            sequence = "GGGS" * 10

        self.parts["tmd_linker"] = AnnotatedPart(sequence=sequence,
                                                 name=name if name else "TMD Linker",
                                                 seq_annotations=[Annotation("Linker" if not annotation else annotation)])

        return self

    def add_protease_sequence(self, protease_name: str) -> MesaChain:
        proteases = NTEV_DATA
        proteases.update(CTEV_DATA)
        proteases.update(TEVP_DATA)

        if protease_name not in proteases.keys():
            raise ValueError(
                f"{protease_name} is not a valid Protease name. Please only use available NTEV, CTEV or TEVP names")

        self.parts["protease"] = AnnotatedPart(sequence=proteases[protease_name],
                                               name=protease_name,
                                               seq_annotations=[Annotation(name=protease_name)])

        return self

    def add_custom_protease_sequence(self, sequence: str, name: str | None = None,
                                     annotation: str | None = None) -> MesaChain:
        if not sequence:
            raise ValueError("Sequence cannot be None")

        self.parts["protease"] = AnnotatedPart(sequence=sequence,
                                               name=name if name else "Protease",
                                               seq_annotations=[Annotation("Protease" if not annotation else annotation)])

        return self

    def add_prs(self, prs_name: str | None = None) -> MesaChain:
        if not prs_name:
            prs_name = "PRS"

        if prs_name not in PRS_DATA.keys():
            raise ValueError(f"{prs_name} is not a valid PRS name. Please only use available PRS names")

        self.parts["prs"] = AnnotatedPart(sequence=PRS_DATA[prs_name][1],
                                          name=prs_name,
                                          seq_annotations=[Annotation(prs_name)])

        return self

    def add_custom_prs(self, sequence: str, name: str | None = None, annotation: str | None = None) -> MesaChain:
        if not sequence:
            raise ValueError("Protease Recognition Sequence cannot be None")

        self.parts["prs"] = AnnotatedPart(sequence=sequence,
                                          name=name if name else "PRS",
                                          seq_annotations=[Annotation(name="PRS" if not annotation else annotation)])

        return self

    def add_target(self, sequence: str, name: str | None = None, annotation: str | None = None) -> MesaChain:
        if not sequence:
            raise ValueError("Cargo Sequence cannot be None")

        self.parts["cargo"] = AnnotatedPart(sequence=sequence,
                                            name=name if name else "Cargo",
                                            seq_annotations=[Annotation(name="Cargo" if not annotation else annotation)])

        return self

    def add_tmd(self, tmd_name: str) -> MesaChain:
        tmd_name = tmd_name.upper()
        if not tmd_name in TMD_DATA.keys():
            raise ValueError(
                f"{tmd_name} is not a valid TMD name. Please only use available TMD names or use a custom TMD")

        self.parts["tmd"] = AnnotatedPart(sequence=TMD_DATA[tmd_name][1],
                                          name=f"{tmd_name}_TMD",
                                          seq_annotations=[Annotation(f"{tmd_name}_TMD")])

        return self

    def add_custom_tmd(self, sequence: str, name: str | None = None, annotation: str | None = None) -> MesaChain:
        if not sequence:
            raise ValueError("TMD Sequence cannot be None")

        self.parts["tmd"] = AnnotatedPart(sequence=sequence,
                                          name=name if name else "TMD",
                                          seq_annotations=[Annotation(f"{name}_TMD" if not annotation else annotation)])

        return self

    def add_signal_peptide(self, peptide_name: str | None = None) -> MesaChain:
        if not peptide_name:
            peptide_name = "CD4"

        peptide_name = peptide_name.upper()
        if peptide_name not in SIGNAL_SEQS.keys():
            raise ValueError(
                f"{peptide_name} is not a valid peptide name. Please only use available peptide names or use a custom peptide sequence")

        self.parts["signal_peptide"] = AnnotatedPart(sequence=SIGNAL_SEQS[peptide_name][1],
                                                     name=f"{peptide_name}_Signal_Peptide",
                                                     seq_annotations=[Annotation(f"{peptide_name}_Signal_Peptide")])

        return self

    def add_custom_signal_peptide(self, sequence: str, name: str | None = None,
                                  annotation: str | None = None) -> MesaChain:
        if not sequence:
            raise ValueError("Peptide sequence cannot be None")

        self.parts["signal_peptide"] = AnnotatedPart(sequence=sequence,
                                                     name=name if name else "Signal_Peptide",
                                                     seq_annotations=[Annotation(f"{annotation}_Signal_Peptide" if not annotation else annotation)])

        return self

    def add_aip(self, aip_name: str) -> MesaChain:
        aip_name = aip_name.upper()
        if not aip_name in AIP_DATA.keys():
            raise ValueError(
                f"{aip_name} is not a valid AIP name. Please only use available AIP names or use a custom AIP")

        self.parts["aip"] = AnnotatedPart(sequence=AIP_DATA[aip_name][1],
                                          name=f"{aip_name}_AIP",
                                          seq_annotations=[Annotation(f"{aip_name}_AIP")])

        return self

    def add_custom_aip(self, sequence: str, name: str, annotation: str | None = None) -> MesaChain:
        if not sequence:
            raise ValueError("AIP Sequence cannot be None")

        self.parts["aip"] = AnnotatedPart(sequence=sequence,
                                          name=name,
                                          seq_annotations=[Annotation(f"{name}_AIP" if not annotation else annotation)])

        return self

    def remove_component(self, component: str) -> MesaChain:
        if not component:
            raise ValueError("Component cannot be None")

        if component in self.parts.keys():
            self.parts.pop(component)

        else:
            raise ValueError("Component not in current MESA Chain")

        return self

    def to_annotated_part(self, name: str, part_id: str | None=None, description: str | None=None) -> AnnotatedPart:
        sequence: str = ""
        seq_annotations: list[Annotation] = []
        for component in MESA_ORDER:
            if component in self.parts.keys():
                seq_annotations.append(self.parts[component].get_annotations()[0].shift_annotation(len(sequence)))
                sequence += self.parts[component].get_sequence()

                # conditionally add short linker
                match component:
                    case "binder":
                        if "tmd_linker" not in self.parts.keys():
                            sequence += "GGGSGGGS"

                    case "tmd":
                        sequence += "GGGSGGGS"

                    case "protease":
                        if "prs" in self.parts.keys() or "cargo" in self.parts.keys() or "aip" in self.parts.keys():
                            sequence += "GGGSGGGS"

                    case "prs":
                        if "cargo" in self.parts.keys():
                            sequence += "GGGSGGGS"

                    case "cargo":
                        if "aip" in self.parts.keys():
                            sequence += "GGGSGGGS"

                        sequence += "*"

        if not sequence.startswith("M"):
            sequence = "M" + sequence
            for annotation in seq_annotations:
                annotation.shift_annotation(1)

        return AnnotatedPart(sequence=sequence,
                             name=name,
                             part_id=part_id if part_id else name,
                             description=description if description else name,
                             seq_annotations=seq_annotations)

    def to_genbank_string(self) -> str:
        return self.to_annotated_part(name="mesa_chain").to_genbank_string()

    def save_genbank_file(self, file_path: str) -> None:
        self.to_annotated_part(name="mesa_chain").save_genbank_file(file_path)


class MesaAssembly:
    def __init__(self, mesa_chains: dict[str, MesaChain] | None):
        self.mesa_chains: dict[str, MesaChain] = mesa_chains if mesa_chains else {}

    def set_chain(self, name: str, mesa_chain: MesaChain) -> MesaAssembly:
        if not (name and mesa_chain):
            raise ValueError("MESA Chain cannot be None")

        self.mesa_chains[name] = mesa_chain

        return self


if __name__ == "__main__":
    m = MesaChain()
    m.add_tmd("FGFR4")
