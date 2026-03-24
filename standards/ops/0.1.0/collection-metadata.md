# OPS Data Standard — Collection Metadata

Part of the [OPS Data Standard](schema.md) v0.1.0.

---

## Collection Metadata

**Scope:** Per collection
**File format:** YAML
**File path:** `collection_metadata.yaml`

This file captures publication and provenance metadata shared across all experiments in the collection.

#### collection.title

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>collection.title</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>Free-text title for the collection</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>.</td>
</tr>
</tbody>
</table>

#### collection.publication_doi

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Key</strong></td>
<td><code>collection.publication_doi</code></td>
</tr>
<tr>
<td><strong>Description</strong></td>
<td>DOI of the associated publication. Applies to all experiments in the collection.</td>
</tr>
<tr>
<td><strong>Annotator</strong></td>
<td>Submitter MUST annotate if published. Otherwise MUST be <code>null</code>.</td>
</tr>
<tr>
<td><strong>Value</strong></td>
<td><code>String</code>. MUST be a valid DOI URI (e.g., <code>"https://doi.org/10.1016/j.cell.2022.12.009"</code>).</td>
</tr>
</tbody>
</table>

---
