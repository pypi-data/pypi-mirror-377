from hyperargs import Conf, IntArg, StrArg, FloatArg



@Conf.add_dependency('aa', 'bb')
@Conf.add_dependency('bb', 'cc')
class CC(Conf):
    aa: IntArg = IntArg(1)
    bb: IntArg = IntArg(2)
    cc: IntArg = IntArg(3, 0, 400)
    dd: Conf = Conf()
    ee: StrArg = StrArg("hello", env_bind="STR_ARG")
    d: list = [FloatArg(0.1), FloatArg(0.2), FloatArg(0.3), Conf()]

    @Conf.monitor_on('aa')
    def set_cc(self) -> None:
        if self.aa.value() is not None:
            self.cc = self.cc.parse(123 * 3)
            

a = CC.parse_command_line(strict=False)
print(a)