# Protocol: Phase 5 Agent 4 - Validation Script Enhancements & Task Creation

**Date**: 2026-01-18
**Agent ID**: validation-enhancement-agent-2026-01-18-004
**Phase**: 5 (Integration & Tooling)
**Agent Role**: Agent 4 - Validation Script Enhancements & Follow-up Task Creation
**Status**: IN_PROGRESS

---

## Objective

Define validation script enhancements and create follow-up task:
1. Document enhancements needed for validate_meta.py
2. Document enhancements needed for generate_user_needs_status.py
3. Create follow-up task TASK-PROC-010-03 for implementing all Phase 5 changes

---

## Plan Reference

Following plan: `plans_and_protocols/2026-01-18_16_opus_plan_phase5.md`
- Section: Agent 4 (lines 595-783)

---

## Execution Log

### Step 1: Context Gathering (COMPLETE)

**Files Read**:
- ✅ `plans_and_protocols/2026-01-18_16_opus_plan_phase5.md` - Agent 4 specification
- ✅ `goal.md` - Task objective and scope
- ✅ `scripts/validate_meta.py` - Current validation script implementation
- ✅ `scripts/generate_user_needs_status.py` - Current status generator implementation
- ✅ `plans_and_protocols/2026-01-18_19_protocol_phase5_agent3.md` - Agent 3 completion status

**Key Findings**:
- Agent 1: Completed cross-reference documentation in README.md
- Agent 2: Completed three new skill creations
- Agent 3: Completed existing skill enhancements
- Current validate_meta.py: 473 lines, validates requirements.md and goal.md YAML
- Current generate_user_needs_status.py: 365 lines, generates status report for user needs
- Need to define enhancements for both scripts per plan

### Step 2: Define validate_meta.py Enhancements (IN_PROGRESS)

**Plan Specification** (lines 601-653):
- Add new UserNeedsMeta dataclass
- Add validate_user_needs() function
- Add validate_epic_user_needs_references() function
- Add validate_cross_reference_symmetry() function
- Enhance output format

**Enhancement Specification Document**:

Creating detailed specification for validate_meta.py enhancements...

### Step 3: Define generate_user_needs_status.py Enhancements (COMPLETE)

**Plan Specification** (lines 655-681):
- Add cross-reference validation
- Add epic coverage report
- Add orphan detection
- Add completion tracking
- Enhance output sections

**Enhancement Specification Document**: See Product 2 below

### Step 4: Create Follow-Up Task (COMPLETE)

**Plan Specification** (lines 683-773):
- Create task folder structure
- Write goal.md with proper YAML frontmatter
- Reference this plan document

**Actions Taken**:
- ✅ Created task folder: `requirements_tasks/process/AI_rules/requirements_management/user_needs_structure/tasks/2026-01-18_impl_user_needs_skill_integration/`
- ✅ Created plans_and_protocols subfolder
- ✅ Created goal.md with complete YAML frontmatter (task_id: TASK-PROC-010-03)
- ✅ Referenced this plan and all agent protocols
- ✅ Added detailed implementation steps
- ✅ Added testing strategy
- ✅ Added specification references for all components

---

## Work Products

### Product 1: validate_meta.py Enhancement Specification

#### New Data Structures

**UserNeedsMeta Dataclass**:
```python
@dataclass
class UserNeedsMeta:
    """Metadata for user needs documents (personas, scenarios, flows)."""
    id: str  # PERSONA-001, SCEN-001-01, FLOW-001-01-01
    doc_type: str  # persona, scenario, flow
    path: str
    review_status: str  # draft, in_review, approved, deprecated
    parent_id: Optional[str] = None  # For scenarios: persona_id, for flows: scenario_id

    # Flow-specific fields
    implementation_status: Optional[str] = None  # not_started, partial, complete
    implementing_epics: List[str] = field(default_factory=list)  # Epic IDs from flow.md table
```

#### New Validation Functions

**1. validate_user_needs()**

**Purpose**: Find and validate all persona, scenario, and flow files

**Logic**:
```python
def validate_user_needs(self):
    """Find and validate all persona, scenario, flow files."""
    user_needs_root = self.base_path / "requirements_user_needs" / "personas"

    if not user_needs_root.exists():
        self.add_error(str(user_needs_root),
                      "requirements_user_needs/personas/ folder not found",
                      "warning")
        return

    # Pattern matchers
    PERSONA_ID_PATTERN = re.compile(r'^PERSONA-\d{3}$')
    SCENARIO_ID_PATTERN = re.compile(r'^SCEN-\d{3}-\d{2}$')
    FLOW_ID_PATTERN = re.compile(r'^FLOW-\d{3}-\d{2}-\d{2}$')

    # Scan persona directories
    for persona_dir in user_needs_root.iterdir():
        if not persona_dir.is_dir():
            continue

        # Validate persona.md
        persona_file = persona_dir / "persona.md"
        if not persona_file.exists():
            self.add_error(str(persona_dir),
                          "Missing persona.md file", "warning")
            continue

        persona_meta = self._validate_user_needs_file(
            persona_file, "persona", PERSONA_ID_PATTERN
        )
        if persona_meta:
            self.user_needs[persona_meta.id] = persona_meta

        # Scan scenarios
        scenarios_dir = persona_dir / "scenarios"
        if not scenarios_dir.exists():
            continue

        for scenario_dir in scenarios_dir.iterdir():
            if not scenario_dir.is_dir():
                continue

            # Validate scenario.md
            scenario_file = scenario_dir / "scenario.md"
            if not scenario_file.exists():
                self.add_error(str(scenario_dir),
                              "Missing scenario.md file", "warning")
                continue

            scenario_meta = self._validate_user_needs_file(
                scenario_file, "scenario", SCENARIO_ID_PATTERN
            )
            if scenario_meta:
                # Verify parent persona reference
                expected_persona = f"PERSONA-{scenario_meta.id.split('-')[1]}"
                if scenario_meta.parent_id != expected_persona:
                    self.add_error(str(scenario_file),
                                  f"Scenario parent_id mismatch: expected {expected_persona}, got {scenario_meta.parent_id}")
                elif expected_persona not in self.user_needs:
                    self.add_error(str(scenario_file),
                                  f"Parent persona {expected_persona} not found")

                self.user_needs[scenario_meta.id] = scenario_meta

            # Scan user flows
            flows_dir = scenario_dir / "user_flows"
            if not flows_dir.exists():
                continue

            for flow_dir in flows_dir.iterdir():
                if not flow_dir.is_dir():
                    continue

                # Validate flow.md
                flow_file = flow_dir / "flow.md"
                if not flow_file.exists():
                    self.add_error(str(flow_dir),
                                  "Missing flow.md file", "warning")
                    continue

                flow_meta = self._validate_user_needs_file(
                    flow_file, "flow", FLOW_ID_PATTERN
                )
                if flow_meta:
                    # Verify parent scenario reference
                    expected_scenario = f"SCEN-{'-'.join(flow_meta.id.split('-')[1:3])}"
                    if flow_meta.parent_id != expected_scenario:
                        self.add_error(str(flow_file),
                                      f"Flow parent_id mismatch: expected {expected_scenario}, got {flow_meta.parent_id}")
                    elif expected_scenario not in self.user_needs:
                        self.add_error(str(flow_file),
                                      f"Parent scenario {expected_scenario} not found")

                    # Extract implementing epics from flow.md content
                    flow_meta.implementing_epics = self._extract_implementing_epics(flow_file)

                    self.user_needs[flow_meta.id] = flow_meta

def _validate_user_needs_file(self, file_path: Path, doc_type: str, id_pattern) -> Optional[UserNeedsMeta]:
    """Validate a single user needs file and extract metadata."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        self.add_error(str(file_path), f"Could not read file: {e}")
        return None

    # Parse YAML frontmatter
    meta = self.parse_yaml_frontmatter(content)
    if meta is None:
        self.add_error(str(file_path), "No YAML frontmatter found", "warning")
        return None

    # Extract ID based on doc type
    id_field = f"{doc_type}_id"
    doc_id = meta.get(id_field)

    if not doc_id:
        self.add_error(str(file_path), f"Missing '{id_field}' field in frontmatter")
        return None

    # Validate ID format
    if not id_pattern.match(doc_id):
        self.add_error(str(file_path), f"Invalid {doc_type} ID format: {doc_id}")

    # Check for duplicate IDs
    if doc_id in self.user_needs:
        self.add_error(str(file_path),
                      f"Duplicate {doc_type} ID: {doc_id} (also in {self.user_needs[doc_id].path})")

    # Validate review_status
    review_status = meta.get('review_status', '')
    valid_statuses = ['draft', 'in_review', 'approved', 'deprecated']
    if review_status not in valid_statuses:
        self.add_error(str(file_path),
                      f"Invalid review_status: {review_status} (must be one of {valid_statuses})",
                      "warning")

    # Extract parent reference (for scenarios and flows)
    parent_id = None
    if doc_type == 'scenario':
        parent_id = meta.get('persona_id')
        if not parent_id:
            self.add_error(str(file_path), "Missing 'persona_id' field in scenario")
    elif doc_type == 'flow':
        parent_id = meta.get('scenario_id')
        if not parent_id:
            self.add_error(str(file_path), "Missing 'scenario_id' field in flow")

        # Validate implementation_status for flows
        impl_status = meta.get('implementation_status', '')
        valid_impl_statuses = ['not_started', 'partial', 'complete']
        if impl_status not in valid_impl_statuses:
            self.add_error(str(file_path),
                          f"Invalid implementation_status: {impl_status} (must be one of {valid_impl_statuses})",
                          "warning")

    return UserNeedsMeta(
        id=doc_id,
        doc_type=doc_type,
        path=str(file_path),
        review_status=review_status,
        parent_id=parent_id,
        implementation_status=meta.get('implementation_status') if doc_type == 'flow' else None
    )

def _extract_implementing_epics(self, flow_file: Path) -> List[str]:
    """Extract epic/feature IDs from flow.md 'Implementing Epics/Features' table."""
    try:
        content = flow_file.read_text(encoding='utf-8')
    except:
        return []

    # Look for "Implementing Epics/Features" section
    # Parse markdown table to extract epic IDs
    epic_ids = []
    in_table = False

    for line in content.split('\n'):
        if '## Implementing Epics/Features' in line or '## Related Epic/Feature' in line:
            in_table = True
            continue
        if in_table:
            if line.startswith('##'):  # Next section
                break
            # Look for epic references like EPIC-THER-001 or REQ-FUNC-001
            matches = re.findall(r'(REQ-[A-Z]+-\d{3}|EPIC-[A-Z]+-\d{3})', line)
            epic_ids.extend(matches)

    return list(set(epic_ids))  # Remove duplicates
```

**2. validate_epic_user_needs_references()**

**Purpose**: Validate user_needs field in epic/feature requirements.md

**Logic**:
```python
def validate_epic_user_needs_references(self):
    """Validate user_needs field in epic/feature requirements.md."""
    for req_id, req in self.requirements.items():
        # Read requirements.md to check for user_needs field
        try:
            with open(req.path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            continue

        meta = self.parse_yaml_frontmatter(content)
        if not meta or 'user_needs' not in meta:
            continue  # user_needs is optional

        user_needs = meta['user_needs']

        # Validate implements_flows
        implements_flows = user_needs.get('implements_flows', [])
        for flow_ref in implements_flows:
            if isinstance(flow_ref, dict):
                flow_id = flow_ref.get('id', '')
            else:
                flow_id = flow_ref

            if not flow_id:
                self.add_error(req.path, "Empty flow ID in user_needs.implements_flows")
                continue

            # Check flow exists
            if flow_id not in self.user_needs:
                self.add_error(req.path,
                              f"user_needs.implements_flows references non-existent flow: {flow_id}")
            else:
                flow_meta = self.user_needs[flow_id]

                # Warn if flow not approved
                if flow_meta.review_status != 'approved':
                    self.add_error(req.path,
                                  f"Epic references flow {flow_id} which has review_status: {flow_meta.review_status}",
                                  "warning")

                # Validate coverage vs implementation_status
                if isinstance(flow_ref, dict):
                    claimed_coverage = flow_ref.get('coverage', 'not_started')
                    actual_impl = flow_meta.implementation_status or 'not_started'

                    # Consistency check (not strict, just warning)
                    if claimed_coverage == 'complete' and actual_impl != 'complete':
                        self.add_error(req.path,
                                      f"Epic claims complete coverage of {flow_id} but flow has implementation_status: {actual_impl}",
                                      "warning")

        # Validate addresses_scenarios
        addresses_scenarios = user_needs.get('addresses_scenarios', [])
        for scenario_id in addresses_scenarios:
            if scenario_id not in self.user_needs:
                self.add_error(req.path,
                              f"user_needs.addresses_scenarios references non-existent scenario: {scenario_id}")
            else:
                scenario_meta = self.user_needs[scenario_id]
                if scenario_meta.review_status != 'approved':
                    self.add_error(req.path,
                                  f"Epic references scenario {scenario_id} which has review_status: {scenario_meta.review_status}",
                                  "warning")

        # Validate personas_served
        personas_served = user_needs.get('personas_served', [])
        for persona_id in personas_served:
            if persona_id not in self.user_needs:
                self.add_error(req.path,
                              f"user_needs.personas_served references non-existent persona: {persona_id}")
            else:
                persona_meta = self.user_needs[persona_id]
                if persona_meta.review_status != 'approved':
                    self.add_error(req.path,
                                  f"Epic references persona {persona_id} which has review_status: {persona_meta.review_status}",
                                  "warning")
```

**3. validate_cross_reference_symmetry()**

**Purpose**: Check bidirectional references are symmetric

**Logic**:
```python
def validate_cross_reference_symmetry(self):
    """Check bidirectional references are symmetric."""
    # For each flow that lists implementing epics
    for flow_id, flow_meta in self.user_needs.items():
        if flow_meta.doc_type != 'flow':
            continue

        for epic_id in flow_meta.implementing_epics:
            # Check if epic exists
            if epic_id not in self.requirements:
                self.add_error(flow_meta.path,
                              f"Flow references epic {epic_id} which doesn't exist in requirements")
                continue

            # Check if epic references this flow back
            epic = self.requirements[epic_id]
            try:
                with open(epic.path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                continue

            meta = self.parse_yaml_frontmatter(content)
            if not meta or 'user_needs' not in meta:
                self.add_error(flow_meta.path,
                              f"Flow {flow_id} lists epic {epic_id} but epic doesn't have user_needs field",
                              "warning")
                continue

            # Check if flow_id is in implements_flows
            user_needs = meta['user_needs']
            implements_flows = user_needs.get('implements_flows', [])

            flow_referenced = False
            for flow_ref in implements_flows:
                ref_id = flow_ref.get('id') if isinstance(flow_ref, dict) else flow_ref
                if ref_id == flow_id:
                    flow_referenced = True
                    break

            if not flow_referenced:
                self.add_error(flow_meta.path,
                              f"Flow {flow_id} lists epic {epic_id} but epic doesn't reference flow back (asymmetric reference)",
                              "warning")
```

#### Enhanced Output Format

**New Output Section**:
```python
def run(self) -> Tuple[int, int]:
    """Run all validations. Returns (error_count, warning_count)."""
    print("=" * 60)
    print("META INFORMATION VALIDATION")
    print("=" * 60)
    print()

    # NEW: Validate user needs first
    print("Scanning user needs documents...")
    self.validate_user_needs()

    persona_count = len([m for m in self.user_needs.values() if m.doc_type == 'persona'])
    scenario_count = len([m for m in self.user_needs.values() if m.doc_type == 'scenario'])
    flow_count = len([m for m in self.user_needs.values() if m.doc_type == 'flow'])

    print(f"  Found {persona_count} personas")
    print(f"  Found {scenario_count} scenarios")
    print(f"  Found {flow_count} flows")

    print("\nScanning requirements.md files...")
    self.validate_requirements()
    print(f"  Found {len(self.requirements)} requirements with valid frontmatter")

    print("\nScanning goal.md files...")
    self.validate_tasks()
    print(f"  Found {len(self.tasks)} tasks with valid frontmatter")

    print("\nValidating coverage references...")
    self.validate_coverage_references()

    # NEW: Validate user needs references
    print("\nValidating user needs references...")
    self.validate_epic_user_needs_references()

    print("\nValidating cross-reference symmetry...")
    self.validate_cross_reference_symmetry()

    # Count errors and warnings (existing code)
    # ... rest of existing output code ...

    # NEW: Add user needs summary before final summary
    if self.user_needs:
        print("\n=== USER NEEDS SUMMARY ===")

        # Status breakdown
        status_counts = {'draft': 0, 'in_review': 0, 'approved': 0, 'deprecated': 0}
        for meta in self.user_needs.values():
            status = meta.review_status
            if status in status_counts:
                status_counts[status] += 1

        print(f"Personas: {persona_count} (approved: {len([m for m in self.user_needs.values() if m.doc_type == 'persona' and m.review_status == 'approved'])})")
        print(f"Scenarios: {scenario_count} (approved: {len([m for m in self.user_needs.values() if m.doc_type == 'scenario' and m.review_status == 'approved'])})")
        print(f"Flows: {flow_count} (approved: {len([m for m in self.user_needs.values() if m.doc_type == 'flow' and m.review_status == 'approved'])})")
        print()
```

#### Constructor Changes

**Add user_needs dictionary**:
```python
def __init__(self, base_path: Path, verbose: bool = False):
    self.base_path = base_path
    self.verbose = verbose
    self.errors: List[ValidationError] = []
    self.requirements: Dict[str, RequirementMeta] = {}
    self.tasks: Dict[str, TaskMeta] = {}
    self.user_needs: Dict[str, UserNeedsMeta] = {}  # NEW: id -> UserNeedsMeta
```

---

### Product 2: generate_user_needs_status.py Enhancement Specification

#### New Features

**1. Cross-Reference Validation**

**Purpose**: Check that all references in flow.md are valid

**Implementation**:
```python
def validate_cross_references(self):
    """Validate all cross-references in user needs documents."""
    issues = []

    for flow in self.flows:
        flow_id = flow.get('flow_id', 'UNKNOWN')

        # Parse implementing epics from flow content
        flow_file = self.root_dir / flow['_file_path']
        try:
            with open(flow_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            continue

        # Extract epic references
        epic_refs = self._extract_epic_references(content)

        # Check if epic files exist
        for epic_id in epic_refs:
            epic_path = self._find_epic_path(epic_id)
            if not epic_path:
                issues.append({
                    'flow': flow_id,
                    'issue': f"References non-existent epic: {epic_id}",
                    'severity': 'error'
                })
            else:
                # Check if epic references flow back
                if not self._epic_references_flow(epic_path, flow_id):
                    issues.append({
                        'flow': flow_id,
                        'issue': f"Epic {epic_id} doesn't reference flow back (asymmetric)",
                        'severity': 'warning'
                    })

    return issues

def _extract_epic_references(self, content: str) -> List[str]:
    """Extract epic IDs from flow content."""
    epic_ids = []
    matches = re.findall(r'(REQ-[A-Z]+-\d{3}|EPIC-[A-Z]+-\d{3})', content)
    return list(set(matches))

def _find_epic_path(self, epic_id: str) -> Optional[Path]:
    """Find path to epic requirements.md file."""
    # Search requirements_tasks/ for matching requirements.md
    req_root = self.root_dir.parent / "requirements_tasks"
    if not req_root.exists():
        return None

    for req_file in req_root.rglob("requirements.md"):
        try:
            with open(req_file, 'r', encoding='utf-8') as f:
                content = f.read()
            if f"id: {epic_id}" in content or f"id: '{epic_id}'" in content:
                return req_file
        except:
            continue
    return None

def _epic_references_flow(self, epic_path: Path, flow_id: str) -> bool:
    """Check if epic references the given flow in user_needs field."""
    try:
        with open(epic_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return flow_id in content
    except:
        return False
```

**2. Epic Coverage Report**

**Purpose**: Show which epics/features implement which flows

**Implementation**:
```python
def _generate_epic_coverage(self) -> list:
    """Generate epic/feature coverage report."""
    lines = []
    lines.append("## Epic/Feature Coverage")
    lines.append("")

    # Build mapping: epic_id -> flows it implements
    epic_to_flows = defaultdict(list)

    for flow in self.flows:
        flow_id = flow.get('flow_id', 'UNKNOWN')
        flow_name = flow.get('name', 'Unnamed')
        impl_status = flow.get('implementation_status', 'unknown')

        # Extract epic references from flow
        flow_file = self.root_dir / flow['_file_path']
        try:
            with open(flow_file, 'r', encoding='utf-8') as f:
                content = f.read()
            epic_refs = self._extract_epic_references(content)

            for epic_id in epic_refs:
                epic_to_flows[epic_id].append({
                    'flow_id': flow_id,
                    'flow_name': flow_name,
                    'impl_status': impl_status
                })
        except:
            continue

    if not epic_to_flows:
        lines.append("*No epic/feature coverage mappings found*")
        lines.append("")
        return lines

    # Generate table
    lines.append("| Epic/Feature | Flows Implemented | Implementation Status |")
    lines.append("|--------------|-------------------|----------------------|")

    for epic_id in sorted(epic_to_flows.keys()):
        flows = epic_to_flows[epic_id]
        flow_list = ", ".join([f"{f['flow_id']}" for f in flows])

        # Calculate aggregate status
        statuses = [f['impl_status'] for f in flows]
        if all(s == 'complete' for s in statuses):
            agg_status = "complete"
        elif all(s == 'not_started' for s in statuses):
            agg_status = "not_started"
        else:
            agg_status = "partial"

        lines.append(f"| {epic_id} | {flow_list} | {agg_status} |")

    lines.append("")
    return lines
```

**3. Orphan Detection**

**Purpose**: Find user flows not referenced by any epic

**Implementation**:
```python
def _generate_orphan_flows(self) -> list:
    """Generate list of orphan flows (not referenced by any epic)."""
    lines = []
    lines.append("## Orphan Flows (Not Referenced by Any Epic)")
    lines.append("")

    orphans = []

    # Build set of all epics that reference flows
    referenced_flows = set()

    req_root = self.root_dir.parent / "requirements_tasks"
    if req_root.exists():
        for req_file in req_root.rglob("requirements.md"):
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract FLOW-XXX-XX-XX references
                flow_refs = re.findall(r'FLOW-\d{3}-\d{2}-\d{2}', content)
                referenced_flows.update(flow_refs)
            except:
                continue

    # Find orphan flows
    for flow in self.flows:
        flow_id = flow.get('flow_id', 'UNKNOWN')
        if flow_id not in referenced_flows:
            orphans.append({
                'flow_id': flow_id,
                'flow_name': flow.get('name', 'Unnamed'),
                'impl_status': flow.get('implementation_status', 'unknown')
            })

    if not orphans:
        lines.append("*All flows are referenced by at least one epic*")
        lines.append("")
    else:
        for orphan in sorted(orphans, key=lambda x: x['flow_id']):
            lines.append(f"- **{orphan['flow_id']}** ({orphan['flow_name']}) - Status: {orphan['impl_status']}")
        lines.append("")

    return lines
```

**4. Completion Tracking**

**Purpose**: Show percentage of flows with implementation_status = complete

**Implementation**:
```python
def _generate_implementation_progress(self) -> list:
    """Generate implementation progress report."""
    lines = []
    lines.append("## Implementation Progress")
    lines.append("")

    if not self.flows:
        lines.append("*No flows found*")
        lines.append("")
        return lines

    # Count by implementation_status
    status_counts = defaultdict(int)
    for flow in self.flows:
        status = flow.get('implementation_status', 'unknown')
        status_counts[status] += 1

    total = len(self.flows)
    complete = status_counts.get('complete', 0)
    partial = status_counts.get('partial', 0)
    not_started = status_counts.get('not_started', 0)

    complete_pct = (complete / total * 100) if total > 0 else 0
    partial_pct = (partial / total * 100) if total > 0 else 0
    not_started_pct = (not_started / total * 100) if total > 0 else 0

    lines.append(f"**Total Flows**: {total}")
    lines.append("")
    lines.append(f"- Complete: {complete} ({complete_pct:.1f}%)")
    lines.append(f"- Partial: {partial} ({partial_pct:.1f}%)")
    lines.append(f"- Not Started: {not_started} ({not_started_pct:.1f}%)")
    lines.append("")

    # Progress bar (ASCII)
    bar_width = 50
    complete_width = int(complete_pct / 100 * bar_width)
    partial_width = int(partial_pct / 100 * bar_width)

    bar = "█" * complete_width + "▓" * partial_width + "░" * (bar_width - complete_width - partial_width)
    lines.append(f"```\n{bar}\n```")
    lines.append("")

    return lines
```

#### Enhanced Report Structure

**Updated generate_report() method**:
```python
def generate_report(self) -> str:
    """Generate the status report."""
    lines = []
    lines.append("# User Needs Status Report")
    lines.append("")
    lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Summary statistics (existing)
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total Personas**: {len(self.personas)}")
    lines.append(f"- **Total Scenarios**: {len(self.scenarios)}")
    lines.append(f"- **Total User Flows**: {len(self.flows)}")
    lines.append("")

    # NEW: Implementation progress
    lines.extend(self._generate_implementation_progress())

    # Review status breakdown (existing)
    lines.extend(self._generate_status_summary())

    # NEW: Epic coverage
    lines.extend(self._generate_epic_coverage())

    # NEW: Orphan flows
    lines.extend(self._generate_orphan_flows())

    # NEW: Cross-reference warnings
    issues = self.validate_cross_references()
    if issues:
        lines.append("## Cross-Reference Warnings")
        lines.append("")
        for issue in issues:
            severity_marker = "⚠️" if issue['severity'] == 'warning' else "❌"
            lines.append(f"- {severity_marker} {issue['flow']}: {issue['issue']}")
        lines.append("")

    # Documents by status (existing)
    lines.extend(self._generate_documents_by_status())

    # Recently modified (existing)
    lines.extend(self._generate_recently_modified())

    # Pending review (existing)
    lines.extend(self._generate_pending_review())

    return "\n".join(lines)
```

---

## Decisions & Trade-offs

### Decision 1: validate_meta.py - Separate user_needs dictionary
**Choice**: Add separate `self.user_needs` dictionary instead of merging with `self.requirements`
**Reason**: Different data structures (UserNeedsMeta vs RequirementMeta), different ID formats
**Trade-off**: More memory usage, but cleaner separation of concerns

### Decision 2: Asymmetric reference severity
**Choice**: Treat asymmetric references as warnings, not errors
**Reason**: Allows work to proceed while flagging potential issues
**Trade-off**: User must pay attention to warnings

### Decision 3: generate_user_needs_status.py - File system scanning
**Choice**: Scan requirements_tasks/ file system to find epic references
**Reason**: No central index of epics yet, must discover from files
**Trade-off**: Slower performance, but no additional infrastructure needed

### Decision 4: Implementation status calculation
**Choice**: Aggregate epic implementation status from flow statuses
**Reason**: Epic coverage depends on all flows it implements
**Trade-off**: Doesn't account for partial step coverage within flows

---

## Blockers & Issues

None encountered.

---

## Quality Criteria Checklist

From plan (lines 775-780):
- ✅ validate_meta.py enhancement specification complete
- ✅ generate_user_needs_status.py enhancement specification complete
- ✅ Follow-up task folder created
- ✅ goal.md has proper YAML frontmatter
- ✅ Task references this plan document

---

## Files Created

1. ✅ `plans_and_protocols/2026-01-18_20_protocol_phase5_agent4.md` - This protocol file
2. ✅ `../2026-01-18_impl_user_needs_skill_integration/goal.md` - Follow-up task goal file
3. ✅ `../2026-01-18_impl_user_needs_skill_integration/plans_and_protocols/` - Plans folder (empty, ready for implementation protocols)

---

## Summary

### Work Completed

**Agent 4 Objectives: ALL COMPLETE**

1. **Validation Script Enhancement Specifications** ✅
   - validate_meta.py: Complete specification with 3 new validation functions
   - generate_user_needs_status.py: Complete specification with 4 new report sections

2. **Follow-up Task Creation** ✅
   - Task TASK-PROC-010-03 created with proper structure
   - Comprehensive goal.md with all required YAML metadata
   - Detailed implementation steps and testing strategy
   - Complete references to all Phase 5 planning documents

### Work Products Delivered

**Product 1: validate_meta.py Enhancement Specification**
- **UserNeedsMeta dataclass**: Tracks persona/scenario/flow metadata
- **validate_user_needs()**: Scans and validates all user needs files
  - ID format validation (PERSONA-XXX, SCEN-XXX-XX, FLOW-XXX-XX-XX)
  - Parent reference validation
  - Review status validation
  - Duplicate ID detection
- **validate_epic_user_needs_references()**: Validates epic requirements.md user_needs fields
  - implements_flows[] validation
  - addresses_scenarios[] validation
  - personas_served[] validation
  - Review status warnings
- **validate_cross_reference_symmetry()**: Detects asymmetric references
  - Flow→Epic references checked against Epic→Flow references
  - Warnings for one-way references
- **Enhanced output**: User needs summary section with status breakdown

**Product 2: generate_user_needs_status.py Enhancement Specification**
- **Cross-reference validation**: Checks all flow→epic references are valid
- **Epic coverage report**: Shows which epics implement which flows
  - Table format with aggregated implementation status
- **Orphan flow detection**: Identifies flows not referenced by any epic
- **Implementation progress tracking**: Percentage completion with visual progress bar
- **Enhanced report structure**: 4 new sections added to STATUS.md

**Product 3: Follow-up Task TASK-PROC-010-03**
- **Complete task structure**: Folder, plans_and_protocols, goal.md
- **Proper YAML frontmatter**: All required fields including task_id, dependencies, covers
- **Detailed scope**: 8 implementation components (3 new skills, 3 enhanced skills, 2 scripts)
- **Implementation guidance**: Phase-by-phase steps with testing strategy
- **Comprehensive references**: Links to all specifications across 4 agent protocols

### Quality Criteria Status

From plan (lines 775-780):
- ✅ validate_meta.py enhancement specification complete
- ✅ generate_user_needs_status.py enhancement specification complete
- ✅ Follow-up task folder created
- ✅ goal.md has proper YAML frontmatter
- ✅ Task references this plan document

**ALL QUALITY CRITERIA MET**

### Design Highlights

**Design 1: Separation of Concerns**
- validate_meta.py gets new `self.user_needs` dictionary separate from `self.requirements`
- Clean separation between requirements_tasks and requirements_user_needs validation
- Different ID formats handled by different dataclasses

**Design 2: Progressive Validation**
- validate_user_needs() runs first, builds index
- validate_epic_user_needs_references() uses index to check references
- validate_cross_reference_symmetry() checks bidirectional consistency
- Layered approach catches different types of issues

**Design 3: Comprehensive Coverage Reporting**
- generate_user_needs_status.py enhanced with 4 new report sections
- Combines metadata scanning with file system traversal
- Visual progress tracking with ASCII progress bar
- Actionable warnings for missing or asymmetric references

**Design 4: Implementation-Ready Task**
- TASK-PROC-010-03 structured for easy handoff
- Each component has specific line number references to specs
- Testing strategy included for each phase
- Dependencies clearly documented

### Integration with Phase 5

**Agent 4 completes the final piece of Phase 5 planning**:
- Agent 1: Cross-reference documentation (README.md updates) ✅
- Agent 2: New skill specifications (create-persona, create-scenario, create-user-flow) ✅
- Agent 3: Existing skill enhancements (setup-task, verify-quality, explore-requirements) ✅
- **Agent 4**: Validation scripts + Implementation task ✅

**Phase 5 is now fully planned and ready for implementation via TASK-PROC-010-03**

### Next Steps

**For User**:
1. Review TASK-PROC-010-03 goal.md and specifications
2. Approve or request changes to validation script enhancements
3. Execute TASK-PROC-010-03 to implement all Phase 5 components

**For Implementation Agent**:
1. Read TASK-PROC-010-03 goal.md
2. Follow phase-by-phase implementation steps
3. Test each component as specified
4. Log progress to protocol in plans_and_protocols folder

---

**Status**: COMPLETE
**Agent ID**: validation-enhancement-agent-2026-01-18-004
**Completion Time**: 2026-01-18
**All Quality Criteria Met**: YES
**All Deliverables Complete**: YES
