# Build stage
FROM rust:1.89 AS builder
WORKDIR /usr/src/app

# Install refinery-cli

# Pre-build dependencies
COPY Cargo.toml Cargo.lock ./
RUN mkdir src && echo "fn main() {}" > src/main.rs
RUN cargo install refinery_cli
RUN cargo build --release
RUN rm -rf src

# Copy source and build
COPY . .
RUN cargo build --release

# Runtime stage
FROM debian:bullseye-slim
WORKDIR /usr/src/app

# Copy refinery-cli from builder
COPY --from=builder /root/.cargo/bin/refinery /usr/local/bin/refinery

# Copy binary from builder
COPY --from=builder /usr/src/app/target/release/headless-api .

# Copy migrations and config
COPY migrations ./migrations
COPY refinery.toml .

# Copy entrypoint script
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
