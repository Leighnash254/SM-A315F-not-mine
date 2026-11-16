import os
import sys

path = 'drivers/kernelsu/pkg_observer.c'
if not os.path.exists(path):
    print(f'{path} not found!')
    sys.exit(0)

with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

target = """static const struct fsnotify_ops ksu_ops = {
	.handle_inode_event = ksu_handle_inode_event,
};

static int add_mark_on_inode(struct inode *inode, u32 mask,
			     struct fsnotify_mark **out)
{
	struct fsnotify_mark *m;

	m = kzalloc(sizeof(*m), GFP_KERNEL);
	if (!m)
		return -ENOMEM;

	fsnotify_init_mark(m, g);
	m->mask = mask;

	if (fsnotify_add_inode_mark(m, inode, 0)) {
		fsnotify_put_mark(m);
		return -EINVAL;
	}
	*out = m;
	return 0;
}"""

compat_code = """#if LINUX_VERSION_CODE < KERNEL_VERSION(5, 9, 0)
static int ksu_handle_event(struct fsnotify_group *group,
			    struct inode *to_tell,
			    struct fsnotify_mark *inode_mark,
			    struct fsnotify_mark *vfsmount_mark,
			    u32 mask, const void *data, int data_type,
			    const unsigned char *file_name, u32 cookie,
			    struct fsnotify_iter_info *iter_info)
{
	if (!file_name)
		return 0;
	if (mask & FS_ISDIR)
		return 0;
	if (!strcmp((const char *)file_name, "packages.list")) {
		pr_info("packages.list detected: %d\\n", mask);
		track_throne();
	}
	return 0;
}

static const struct fsnotify_ops ksu_ops = {
	.handle_event = ksu_handle_event,
};

static int add_mark_on_inode(struct inode *inode, u32 mask,
			     struct fsnotify_mark **out)
{
	struct fsnotify_mark *m;

	m = kzalloc(sizeof(*m), GFP_KERNEL);
	if (!m)
		return -ENOMEM;

	fsnotify_init_mark(m, g);
	m->mask = mask;

	if (fsnotify_add_mark(m, inode, NULL, 0)) {
		fsnotify_put_mark(m);
		return -EINVAL;
	}
	*out = m;
	return 0;
}
#else
static const struct fsnotify_ops ksu_ops = {
	.handle_inode_event = ksu_handle_inode_event,
};

static int add_mark_on_inode(struct inode *inode, u32 mask,
			     struct fsnotify_mark **out)
{
	struct fsnotify_mark *m;

	m = kzalloc(sizeof(*m), GFP_KERNEL);
	if (!m)
		return -ENOMEM;

	fsnotify_init_mark(m, g);
	m->mask = mask;

	if (fsnotify_add_inode_mark(m, inode, 0)) {
		fsnotify_put_mark(m);
		return -EINVAL;
	}
	*out = m;
	return 0;
}
#endif"""

if target in code:
    code = code.replace(target, compat_code)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)
    print('pkg_observer.c successfully patched for Linux 4.14')
else:
    print('Warning: Target block not found in pkg_observer.c!')
