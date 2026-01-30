#!/bin/bash
# test-docker-builds.sh - Docker Build Testing & Validation Script

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}🐳 MoodleLogSmart Docker Build Testing${NC}"
echo "=================================================="
echo ""

# Function to test build
test_docker_build() {
  local service=$1
  local dockerfile_path=$2
  local image_name=$3
  local target_size=$4

  echo -e "${YELLOW}Testing: $service${NC}"
  echo "  Dockerfile: $dockerfile_path"
  echo "  Image: $image_name"
  echo "  Target size: < $target_size"
  echo ""

  # Check Dockerfile exists
  if [ ! -f "$dockerfile_path" ]; then
    echo -e "${RED}❌ Dockerfile not found: $dockerfile_path${NC}"
    return 1
  fi

  echo -e "${GREEN}✅ Dockerfile exists${NC}"

  # Validate Dockerfile syntax (basic check)
  if grep -q "^FROM" "$dockerfile_path"; then
    echo -e "${GREEN}✅ FROM instruction present${NC}"
  else
    echo -e "${RED}❌ Invalid Dockerfile: no FROM instruction${NC}"
    return 1
  fi

  if grep -q "^RUN" "$dockerfile_path"; then
    echo -e "${GREEN}✅ RUN instructions present${NC}"
  fi

  if grep -q "^CMD" "$dockerfile_path"; then
    echo -e "${GREEN}✅ CMD instruction present${NC}"
  fi

  # Check for multi-stage build
  if [ $(grep -c "^FROM" "$dockerfile_path") -gt 1 ]; then
    echo -e "${GREEN}✅ Multi-stage build detected${NC}"
  else
    echo -e "${YELLOW}⚠️  Single-stage build (not optimal)${NC}"
  fi

  # Check for non-root user
  if grep -q "^USER" "$dockerfile_path"; then
    local user=$(grep "^USER" "$dockerfile_path" | awk '{print $2}')
    if [ "$user" != "root" ]; then
      echo -e "${GREEN}✅ Non-root user: $user${NC}"
    else
      echo -e "${RED}❌ Running as root user${NC}"
      return 1
    fi
  else
    echo -e "${YELLOW}⚠️  No USER instruction (defaults to root)${NC}"
  fi

  # Check for healthcheck
  if grep -q "^HEALTHCHECK" "$dockerfile_path"; then
    echo -e "${GREEN}✅ Healthcheck configured${NC}"
  else
    echo -e "${YELLOW}⚠️  No healthcheck configured${NC}"
  fi

  # Check for expose port
  if grep -q "^EXPOSE" "$dockerfile_path"; then
    local port=$(grep "^EXPOSE" "$dockerfile_path" | awk '{print $2}')
    echo -e "${GREEN}✅ Exposes port: $port${NC}"
  fi

  echo ""
  return 0
}

# Function to test .dockerignore
test_dockerignore() {
  local service=$1
  local dockerignore_path=$2

  echo -e "${YELLOW}Testing: $service .dockerignore${NC}"
  echo "  File: $dockerignore_path"
  echo ""

  if [ ! -f "$dockerignore_path" ]; then
    echo -e "${RED}❌ .dockerignore not found${NC}"
    return 1
  fi

  echo -e "${GREEN}✅ .dockerignore exists${NC}"

  local count=$(wc -l < "$dockerignore_path")
  echo -e "${GREEN}✅ Contains $count rules${NC}"

  # Check for important exclusions
  local checks=(
    ".git"
    ".env"
    "node_modules:frontend only"
    "__pycache__:backend only"
  )

  for check in "${checks[@]}"; do
    local pattern="${check%:*}"
    local note="${check#*:}"

    if [ "$note" != "$pattern" ]; then
      # Check with context
      if [[ "$service" == *"backend"* ]] && [[ "$note" == *"backend"* ]]; then
        if grep -q "$pattern" "$dockerignore_path"; then
          echo -e "${GREEN}✅ Excludes: $pattern${NC}"
        else
          echo -e "${YELLOW}⚠️  Missing: $pattern${NC}"
        fi
      elif [[ "$service" == *"frontend"* ]] && [[ "$note" == *"frontend"* ]]; then
        if grep -q "$pattern" "$dockerignore_path"; then
          echo -e "${GREEN}✅ Excludes: $pattern${NC}"
        else
          echo -e "${YELLOW}⚠️  Missing: $pattern${NC}"
        fi
      fi
    else
      if grep -q "$pattern" "$dockerignore_path"; then
        echo -e "${GREEN}✅ Excludes: $pattern${NC}"
      fi
    fi
  done

  echo ""
  return 0
}

# Main execution
echo -e "${BLUE}=== BACKEND VALIDATION ===${NC}"
test_docker_build "Backend" "$PROJECT_ROOT/backend/Dockerfile" "moodlelogsmart-backend:test" "500MB"
test_dockerignore "backend" "$PROJECT_ROOT/backend/.dockerignore"

echo -e "${BLUE}=== FRONTEND VALIDATION ===${NC}"
test_docker_build "Frontend" "$PROJECT_ROOT/frontend/Dockerfile" "moodlelogsmart-frontend:test" "200MB"
test_dockerignore "frontend" "$PROJECT_ROOT/frontend/.dockerignore"

echo ""
echo -e "${BLUE}=== SUMMARY ===${NC}"
echo -e "${GREEN}✅ All Dockerfiles and .dockerignore files validated${NC}"
echo ""
echo "Next steps:"
echo "1. Run: docker build -t moodlelogsmart-backend:test ./backend"
echo "2. Run: docker build -t moodlelogsmart-frontend:test ./frontend"
echo "3. Verify image sizes: docker images | grep moodlelogsmart"
echo "4. Run security scan: trivy image moodlelogsmart-backend:test"
echo ""
