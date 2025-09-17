from __future__ import annotations
from Bio import SeqIO
from Bio.SeqFeature import SeqFeature, FeatureLocation
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq
from io import StringIO


class Annotation:
    def __init__(self, name: str, sequence: str, start: int | None=None, stop: int | None=None, part_type: str | None=None) -> None:
        self.name: str = name
        self.start: int = start if start else 0
        self.stop: int = stop if stop else len(sequence)
        self.type: str | None = part_type if part_type else "CDS"

    def shift_annotation(self, amount: int) -> Annotation:
        self.start += amount
        self.stop += amount

        return self

    def to_seq_feature(self) -> SeqFeature:
        return SeqFeature(location=FeatureLocation(self.start, self.stop), type=self.type, qualifiers={"name": self.name})


class AnnotatedPart:
    def __init__(self, sequence: str, name: str, part_id: str | None=None, description: str | None=None, seq_annotations: list[Annotation] | None=None) -> None:
        self.sequence: str = sequence if sequence else ""
        self.annotations: list[Annotation] = seq_annotations if seq_annotations else []
        self.name: str = name if name else "no_name"
        self.part_id: str = part_id if part_id else name
        self.description: str = description if description else name

    def get_sequence(self) -> str:
        return self.sequence

    def get_annotations(self) -> list[Annotation]:
        return self.annotations

    def add_annotation(self, annotation: Annotation) -> AnnotatedPart:
        if self.annotations is None:
            self.annotations = [annotation]
            return self

        self.annotations.append(annotation)

        return self

    def add_annotations(self, seq_annotations: list[Annotation]) -> AnnotatedPart:
        if self.annotations is None:
            self.annotations = seq_annotations
            return self

        self.annotations += seq_annotations

        return self

    def add(self, sequence: str, annotation: Annotation | None=None) -> AnnotatedPart:
        if not self.sequence:
            self.sequence = ""

        if not self.annotations:
            self.annotations = []

        self.sequence += sequence
        if annotation:
            self.annotations.append(annotation)

        return self

    def get_seq_record(self) -> SeqRecord:
        return SeqRecord(Seq(self.sequence), id=self.part_id, name=self.name, description=self.description, features=[
            annotation.to_seq_feature() for annotation in self.annotations], annotations={"molecule_type": "PROTEIN"})

    def to_genbank_string(self) -> str:
        f: StringIO = StringIO()
        SeqIO.write(self.get_seq_record(), f, "genbank")
        return f.getvalue()

    def save_genbank_file(self, file_path: str) -> None:
        content: str = self.to_genbank_string()
        with open(file_path, "w") as f:
            f.write(content)
