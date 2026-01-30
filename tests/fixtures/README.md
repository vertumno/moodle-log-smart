# Test Fixtures for MoodleLogSmart

This directory contains test files for E2E testing.

## Files

### `sample_moodle_log.csv`
- **Description**: Small sample Moodle log file
- **Size**: ~1-2 KB
- **Events**: 100-200 sample events
- **Purpose**: Quick E2E testing
- **Columns**: Time, Event name, Component, User full name

### `large_moodle_log_5000.csv`
- **Description**: Large sample Moodle log file
- **Size**: ~200-300 KB
- **Events**: 5000+ events
- **Purpose**: Performance testing
- **Target**: Processing should complete in < 2 minutes

## Format

Expected CSV format (standard Moodle export):

```
Time,Event name,Component,User full name
1/15/24, 10:30,Course module viewed,File,Student User
1/15/24, 10:35,Submission created,Assignment,Student User
1/15/24, 10:40,Attempt submitted,Quiz,Student User
```

### Supported Columns

- **Time**: Date/time in various formats
- **Event name**: Type of action (e.g., "Course module viewed")
- **Component**: System component (e.g., "File", "Assignment", "Quiz")
- **User full name**: Student/user identifier

## Usage

### Generate Sample Data

```bash
# Create small sample
scripts/test-e2e.sh

# The script will generate sample data if not found
```

### E2E Testing

```bash
./scripts/test-e2e.sh        # Run all tests with sample file
./scripts/test-e2e.sh -v     # Verbose mode
./scripts/test-e2e.sh --no-cleanup  # Keep containers running after test
```

## Creating Custom Test Data

```bash
# Create a test file
cat > tests/fixtures/custom_log.csv << 'EOF'
Time,Event name,Component,User full name
1/15/24, 10:30,Course module viewed,File,Test Student
1/15/24, 10:35,Submission created,Assignment,Test Student
EOF
```

---

**Note**: Test files should NOT be committed to git if they're large. Only sample data should be in the repository.
