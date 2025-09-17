#! /usr/bin/env bash

function bluer_ugv_swallow_debug() {
    local object_name=$(bluer_ai_clarify_object $1 swallow-debug-$(bluer_ai_string_timestamp))

    bluer_ai_eval dryrun=$do_dryrun \
        python3 -m bluer_ugv.swallow \
        debug \
        --object_name $object_name \
        "${@:2}"
}
