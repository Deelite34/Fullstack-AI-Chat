FROM ghcr.io/pnpm/pnpm:11.5.3 
RUN pnpm runtime set node 24 -g


WORKDIR /frontend
 
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .
EXPOSE 5173

CMD ["pnpm", "run", "dev", "--host"]