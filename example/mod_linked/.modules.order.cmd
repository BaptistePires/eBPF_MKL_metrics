cmd_/share/platform/example/mod_linked/modules.order := {   echo /share/platform/example/mod_linked/count.ko; :; } | awk '!x[$$0]++' - > /share/platform/example/mod_linked/modules.order
