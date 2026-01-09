# syntax=docker/dockerfile:1
FROM docker/sandbox-templates:claude-code

# Install uv - the fast Python package manager
RUN <<EOF
curl -LsSf https://astral.sh/uv/install.sh | sh
EOF

# Add uv to PATH for all users
ENV PATH="/home/agent/.local/bin:$PATH"

# Install Python 3.13 via uv and set as default
RUN uv python install 3.13

# Set working directory
WORKDIR /workspace

# Copy project files
COPY --chown=agent:agent pyproject.toml uv.lock* ./

# Install dependencies (including dev dependencies)
RUN uv sync --dev

# Copy the rest of the project
COPY --chown=agent:agent . .

# Default command - start a shell ready for development
CMD ["bash"]
