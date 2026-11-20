#!/usr/bin/env python3
"""Apply the SuSFS fs/namespace.c hunk #1 that fails on Samsung 4.14 trees.

The rest of the patch applies; only the include/declaration block at the top
of the file has mismatching context. This inserts it using anchors instead.
Idempotent, and exits non-zero if an anchor can't be found.
"""
import re
import sys

PATH = "fs/namespace.c"

INCLUDE_BLOCK = """#if defined(CONFIG_KSU_SUSFS_SUS_MOUNT) || defined(CONFIG_KSU_SUSFS_TRY_UMOUNT)
#include <linux/susfs_def.h>
#endif
"""

DECL_BLOCK = """#ifdef CONFIG_KSU_SUSFS_SUS_MOUNT
extern bool susfs_is_current_ksu_domain(void);
extern bool susfs_is_current_zygote_domain(void);

static DEFINE_IDA(susfs_mnt_id_ida);
static DEFINE_IDA(susfs_mnt_group_ida);
static int susfs_mnt_id_start = DEFAULT_SUS_MNT_ID;
static int susfs_mnt_group_start = DEFAULT_SUS_MNT_GROUP_ID;

#define CL_ZYGOTE_COPY_MNT_NS BIT(24) /* used by copy_mnt_ns() */
#define CL_COPY_MNT_NS BIT(25) /* used by copy_mnt_ns() */
#endif

#ifdef CONFIG_KSU_SUSFS_AUTO_ADD_SUS_KSU_DEFAULT_MOUNT
extern void susfs_auto_add_sus_ksu_default_mount(const char __user *to_pathname);
bool susfs_is_auto_add_sus_ksu_default_mount_enabled = true;
#endif
#ifdef CONFIG_KSU_SUSFS_AUTO_ADD_SUS_BIND_MOUNT
extern int susfs_auto_add_sus_bind_mount(const char *pathname, struct path *path_target);
bool susfs_is_auto_add_sus_bind_mount_enabled = true;
#endif
#ifdef CONFIG_KSU_SUSFS_AUTO_ADD_TRY_UMOUNT_FOR_BIND_MOUNT
extern void susfs_auto_add_try_umount_for_bind_mount(struct path *path);
bool susfs_is_auto_add_try_umount_for_bind_mount_enabled = true;
#endif

"""

src = open(PATH).read()

if "#include <linux/susfs_def.h>" not in src:
    m = re.search(r'^#include "pnode\.h"', src, re.M)
    if not m:
        sys.exit('anchor not found: #include "pnode.h"')
    src = src[:m.start()] + INCLUDE_BLOCK + "\n" + src[m.start():]
    print("inserted susfs_def.h include")

if "static DEFINE_IDA(susfs_mnt_id_ida);" not in src:
    m = re.search(
        r"^(/\* Maximum number of mounts in a mount namespace \*/\n)?unsigned int sysctl_mount_max",
        src,
        re.M,
    )
    if not m:
        sys.exit("anchor not found: sysctl_mount_max")
    src = src[:m.start()] + DECL_BLOCK + src[m.start():]
    print("inserted SuSFS declarations")

open(PATH, "w").write(src)
