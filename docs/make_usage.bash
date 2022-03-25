#!/usr/bin/env bash
set -ue${DEBUG+xv}
docs_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || die "Couldn't determine the script's running directory" 2
project_dir="$(dirname "${docs_dir:?}")"

output="${docs_dir}/usage.inc"
cat > "${output}" <<EOT
.. code-block:: none
    :emphasize-lines: 1

EOT
help="$("${project_dir}"/decode.py --help)"
sed 's/^\(.\)/    \1/' >> "${output}" <<EOT
${help}
EOT